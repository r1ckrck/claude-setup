-- =============================================================================
-- Pandoc Lua Filter: divs.lua
-- Converts fenced divs to LaTeX environments for callouts and placeholders
-- =============================================================================

-- Callout types we support
local callout_types = {
  note = true,
  tip = true,
  warning = true,
  important = true
}

-- Two-column split layouts. Maps the outer div class to {left_ratio, right_ratio}.
-- Each ratio is a fraction of \linewidth; the gutter (\msgutter) is split
-- evenly between the two columns so the pair fits within \linewidth.
local SPLIT_RATIOS = {
  ['split-50-50'] = { 0.50, 0.50 },
  ['split-35-65'] = { 0.35, 0.65 },
  ['split-65-35'] = { 0.65, 0.35 },
}

-- Render a split-* div: walk the inner ::: col children, emit a list of
-- blocks where the column content is bracketed by RawBlock minipages.
-- Pandoc renders the inner blocks normally, so image paths, callouts,
-- code blocks etc. all keep working inside columns.
-- Errors loudly if structure is wrong so authors notice during the build.
local function render_split(el, ratios)
  local cols = {}
  for _, child in ipairs(el.content) do
    if child.t == 'Div' then
      for _, c in ipairs(child.classes) do
        if c == 'col' then
          cols[#cols + 1] = child
          break
        end
      end
    end
  end

  if #cols ~= 2 then
    error('split-* div requires exactly two ::: col children, got ' .. #cols)
  end

  local lw = string.format('\\dimexpr %.2f\\linewidth - 0.5\\msgutter\\relax', ratios[1])
  local rw = string.format('\\dimexpr %.2f\\linewidth - 0.5\\msgutter\\relax', ratios[2])

  -- mssplitrow is defined in template.tex as a tabular-based environment.
  -- Pandoc emits the inner blocks normally between the begin / & / end
  -- markers, so images, lists, callouts inside columns all just work.
  local out = {
    pandoc.RawBlock('latex',
      '\\begin{mssplitrow}{' .. lw .. '}{' .. rw .. '}'),
  }
  for _, b in ipairs(cols[1].content) do out[#out + 1] = b end
  out[#out + 1] = pandoc.RawBlock('latex', '&')
  for _, b in ipairs(cols[2].content) do out[#out + 1] = b end
  out[#out + 1] = pandoc.RawBlock('latex', '\\end{mssplitrow}')
  return out
end

-- Handle Div elements
function Div(el)
  -- Get the first class (div type)
  local div_type = el.classes[1]
  
  if not div_type then
    return nil
  end
  
  -- Handle two-column split layouts
  if SPLIT_RATIOS[div_type] then
    return render_split(el, SPLIT_RATIOS[div_type])
  end

  -- ::: col is a marker for split-* children; on its own it's a no-op
  -- (render_split consumes them before this filter ever sees them).
  if div_type == 'col' then
    return nil
  end

  -- Handle callouts (note, tip, warning, important)
  if callout_types[div_type] then
    local content = pandoc.write(pandoc.Pandoc(el.content), 'latex')
    return pandoc.RawBlock('latex',
      '\\begin{' .. div_type .. '}\n' ..
      content ..
      '\\end{' .. div_type .. '}'
    )
  end
  
  -- Handle image-placeholder
  if div_type == 'image-placeholder' then
    -- Extract text content from the div
    local text_content = pandoc.utils.stringify(el.content)
    
    -- Escape special LaTeX characters
    text_content = text_content:gsub('%%', '\\%%')
    text_content = text_content:gsub('&', '\\&')
    text_content = text_content:gsub('#', '\\#')
    text_content = text_content:gsub('_', '\\_')
    
    return pandoc.RawBlock('latex',
      '\\begin{imageplaceholder}\n' ..
      text_content ..
      '\n\\end{imageplaceholder}'
    )
  end
  
  -- Return unchanged if not a known type
  return nil
end

local table_break_threshold = 12

local function read_threshold(meta)
  local v = meta.ms_table_break_threshold
  if v then
    local n = tonumber(pandoc.utils.stringify(v))
    if n then table_break_threshold = math.floor(n) end
  end
end

local function count_rows(tbl)
  local n = 0
  if tbl.head and tbl.head.rows then n = n + #tbl.head.rows end
  for _, body in ipairs(tbl.bodies or {}) do
    n = n + #(body.body or {})
    n = n + #(body.head or {})
  end
  if tbl.foot and tbl.foot.rows then n = n + #tbl.foot.rows end
  return n
end

local function longtable_to_tabular(s)
  local prefix, colspec, header, footer, body, suffix = s:match(
    '^(.-)\\begin{longtable}%[%](%b{})%s*\n(.-)\\endhead%s*\n(.-)\\endlastfoot%s*\n(.-)\\end{longtable}(.*)$'
  )
  if not prefix then return nil end
  return prefix .. '\\begin{tabular}' .. colspec .. '\n'
    .. header .. body .. footer
    .. '\\end{tabular}' .. suffix
end

function Table(el)
  if FORMAT ~= 'latex' then return nil end

  local has_caption = el.caption and el.caption.long and #el.caption.long > 0
  local rows = count_rows(el)
  local is_small = rows <= table_break_threshold

  if not is_small and not has_caption then return nil end

  local caption_text = ''
  if has_caption then
    caption_text = pandoc.write(pandoc.Pandoc(el.caption.long), 'latex')
  end

  local stripped = el:clone()
  stripped.caption = pandoc.Caption()
  local table_latex = pandoc.write(pandoc.Pandoc({stripped}), 'latex')

  if is_small then
    local tabular = longtable_to_tabular(table_latex)
    if tabular then
      local out = '\\par\\addvspace{\\mstablebefore}\n'
        .. '\\begin{minipage}{\\linewidth}\n'
        .. tabular
        .. (has_caption and ('\\captionof{table}{' .. caption_text .. '}\n') or '')
        .. '\\end{minipage}\n'
        .. '\\par\\addvspace{\\mstableafter}'
      return pandoc.RawBlock('latex', out)
    end
  end

  table_latex = table_latex:gsub('(\\end{longtable})',
    '%1\n\\captionof{table}{' .. caption_text .. '}')
  table_latex = '\\begingroup\\setlength{\\LTpost}{0pt}\n' .. table_latex .. '\n\\endgroup\\vspace{\\mstableafter}'
  return pandoc.RawBlock('latex', table_latex)
end

-- Handle inline Code elements
function Code(el)
  -- Only for LaTeX output
  if FORMAT ~= 'latex' then
    return nil
  end

  -- Escape special LaTeX characters in code content
  local code_text = el.text
  code_text = code_text:gsub('\\', '\\textbackslash{}')
  code_text = code_text:gsub('{', '\\{')
  code_text = code_text:gsub('}', '\\}')
  code_text = code_text:gsub('%$', '\\$')
  code_text = code_text:gsub('&', '\\&')
  code_text = code_text:gsub('%%', '\\%%')
  code_text = code_text:gsub('#', '\\#')
  code_text = code_text:gsub('_', '\\_')
  code_text = code_text:gsub('%^', '\\textasciicircum{}')
  code_text = code_text:gsub('~', '\\textasciitilde{}')

  -- Use custom inlinecode command
  return pandoc.RawInline('latex', '\\inlinecode{' .. code_text .. '}')
end

-- Handle CodeBlock elements
function CodeBlock(el)
  -- Only for LaTeX output
  if FORMAT ~= 'latex' then
    return nil
  end

  -- Check if this is an ASCII art block
  local is_ascii = false
  for _, class in ipairs(el.classes) do
    if class == 'ascii' or class == 'asciiart' then
      is_ascii = true
      break
    end
  end

  -- For ASCII art blocks, use the asciiart style
  if is_ascii then
    local code_text = el.text
    return pandoc.RawBlock('latex',
      '\\begin{lstlisting}[style=asciiart]\n' ..
      code_text ..
      '\n\\end{lstlisting}'
    )
  end

  -- For regular code blocks, replace Unicode symbols with math mode LaTeX commands
  -- mathescape=true in listings allows $...$ to be rendered as math
  local code_text = el.text
  code_text = code_text:gsub('✓', '$\\checkmark$')
  code_text = code_text:gsub('✗', '$\\times$')

  -- Update the code block text
  el.text = code_text
  return el
end

-- Insert \FloatBarrier before every H2 / H3 header so figures cannot float
-- past a section boundary. Belt-and-braces with \floatplacement{figure}{H} in
-- template.tex. In markset, H1 is the unnumbered document title and H2 is the
-- top-level numbered heading — barriers at H2/H3 catch every real section
-- break without interfering with the cover / TOC structure.
-- The placeins package providing \FloatBarrier is loaded in template.tex.
function Header(el)
  if FORMAT ~= 'latex' then return nil end
  if el.level == 2 or el.level == 3 then
    return {
      pandoc.RawBlock('latex', '\\FloatBarrier'),
      el
    }
  end
  return nil
end

local ANCHOR_TYPES = {
  Table = true, CodeBlock = true,
  BulletList = true, OrderedList = true,
  Div = true, BlockQuote = true,
}

local CHAIN_LIMIT = 5

local function is_split_begin(b)
  return b.t == 'RawBlock' and b.format == 'latex'
    and b.text:find('\\begin{mssplitrow}', 1, true) ~= nil
end

local function is_split_end(b)
  return b.t == 'RawBlock' and b.format == 'latex'
    and b.text:find('\\end{mssplitrow}', 1, true) ~= nil
end

local function inject_nopagebreak(blocks)
  local out = {}
  local i = 1
  while i <= #blocks do
    local block = blocks[i]
    out[#out + 1] = block

    if block.t == 'Header' then
      local j = i + 1
      local bound = 0
      while j <= #blocks and bound < CHAIN_LIMIT do
        local b = blocks[j]
        if b.t == 'Header' then break end
        out[#out + 1] = pandoc.RawBlock('latex', '\\nopagebreak[4]')
        out[#out + 1] = b
        bound = bound + 1
        j = j + 1
        -- A split row is atomic: copy its remaining blocks straight through
        -- (no \nopagebreak between them — those would trigger \topskip
        -- inside the minipage), then end the heading-chain.
        if is_split_begin(b) then
          while j <= #blocks and not is_split_end(blocks[j]) do
            out[#out + 1] = blocks[j]
            j = j + 1
          end
          if j <= #blocks then
            out[#out + 1] = blocks[j]
            j = j + 1
          end
          break
        end
        if ANCHOR_TYPES[b.t] then break end
      end
      i = j
    else
      i = i + 1
    end
  end
  return out
end

local function process_doc(doc)
  doc.blocks = inject_nopagebreak(doc.blocks)
  return doc
end

return {
  { Meta = read_threshold },
  { Div = Div },
  { Table = Table },
  { Code = Code },
  { CodeBlock = CodeBlock },
  { Header = Header },
  { Pandoc = process_doc }
}
