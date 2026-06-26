-- =============================================================================
-- Markset — apply-theme.lua
-- Pandoc Lua filter that:
--   1. Reads the theme map from meta.theme (loaded via --metadata-file)
--   2. Computes a full `tokens` tree from the dials (type.base, type.scale,
--      rhythm.base, heading.space/step, block.*, callout.*, etc.)
--   3. Applies overrides — first theme-level (overrides: block in the YAML),
--      then per-document (theme_overrides: in frontmatter). Overrides route
--      into tokens (for type/rhythm) or into theme (palette/fonts/layout/...)
--      based on their first path segment.
--   4. Resolves {{path}} references inside the palette
--   5. Validates required keys, hex, length, enum
--   6. Emits LaTeX token definitions into header-includes
--   7. Sets boolean layout flags + page meta-vars on meta for template $if(...)$
-- =============================================================================

local utils = pandoc.utils

-- =============================================================================
-- Meta → plain Lua conversion
-- =============================================================================

local function to_plain(v)
  if v == nil then return nil end
  if type(v) == 'boolean' then return v end
  if type(v) == 'number' then return tostring(v) end
  if type(v) == 'string' then return v end

  local ok, ptype = pcall(pandoc.utils.type, v)
  if ok then
    if ptype == 'Inlines' or ptype == 'Blocks' or ptype == 'Inline' or ptype == 'Block' then
      return utils.stringify(v)
    end
    if ptype == 'List' then
      local out = {}
      for i, child in ipairs(v) do out[i] = to_plain(child) end
      return out
    end
  end

  if type(v) == 'table' or type(v) == 'userdata' then
    local strkeys, intkeys = {}, 0
    for k, _ in pairs(v) do
      if type(k) == 'string' and k ~= 't' and k ~= 'tag' then
        strkeys[#strkeys + 1] = k
      elseif type(k) == 'number' then
        intkeys = intkeys + 1
      end
    end
    if #strkeys > 0 then
      local out = {}
      for _, k in ipairs(strkeys) do out[k] = to_plain(v[k]) end
      return out
    end
    if intkeys > 0 then return utils.stringify(v) end
    return {}
  end

  return utils.stringify(v)
end

-- =============================================================================
-- Error collection
-- =============================================================================

local errors = {}
local function err(msg) errors[#errors + 1] = msg end

local function fail_if_errors()
  if #errors > 0 then
    io.stderr:write('\n[markset] theme validation failed:\n')
    for _, e in ipairs(errors) do io.stderr:write('  • ' .. e .. '\n') end
    io.stderr:write('\n')
    error('markset: theme is invalid — see errors above')
  end
end

-- =============================================================================
-- Dot-path helpers
-- =============================================================================

local function split_path(path)
  local parts = {}
  for part in path:gmatch('[^%.]+') do parts[#parts + 1] = part end
  return parts
end

local function get_path(t, path)
  local cur = t
  for _, part in ipairs(split_path(path)) do
    if type(cur) ~= 'table' then return nil end
    cur = cur[part]
  end
  return cur
end

local function set_path(t, parts_or_path, value)
  local parts = type(parts_or_path) == 'string' and split_path(parts_or_path) or parts_or_path
  local cur = t
  for i = 1, #parts - 1 do
    if type(cur[parts[i]]) ~= 'table' then cur[parts[i]] = {} end
    cur = cur[parts[i]]
  end
  cur[parts[#parts]] = value
end

-- =============================================================================
-- Length arithmetic
-- =============================================================================

local function parse_length(s)
  if type(s) ~= 'string' then return nil, nil end
  local n, unit = s:match('^(%-?%d+%.?%d*)([a-zA-Z][a-zA-Z]?)$')
  if n and unit then return tonumber(n), unit end
  return nil, nil
end

local function round_int(n) return math.floor(n + 0.5) end

local function fmt_length(n, unit)
  local r = round_int(n)
  -- If the rounding cost < 0.05pt of precision, accept it. Otherwise keep decimals.
  if math.abs(n - r) < 0.05 then return string.format('%d%s', r, unit) end
  local s = string.format('%.2f%s', n, unit)
  return s:gsub('0+([a-zA-Z])', '%1'):gsub('%.([a-zA-Z])', '%1')
end

-- Multiply a length string by a scalar factor.
local function scale_length(s, factor, fallback_unit)
  local n, unit = parse_length(s)
  if n == nil then return nil end
  return fmt_length(n * factor, unit or fallback_unit or 'pt')
end

-- Parse a length and return just the numeric part (for downstream math).
local function pt_of(s)
  local n, _ = parse_length(s)
  return n
end

-- =============================================================================
-- Colour helpers
-- =============================================================================

local function hex_body(hex)
  if type(hex) ~= 'string' then return '000000' end
  return (hex:gsub('^#', ''))
end

local HEX_RE = '^#[0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F]$'
local LEN_RE = '^%-?%d+%.?%d*[a-zA-Z][a-zA-Z]?$'
local NUM_RE = '^%-?%d+%.?%d*$'

local function validate_hex(value, path)
  if type(value) ~= 'string' or not value:match(HEX_RE) then
    err(path .. ': expected hex like "#rrggbb", got "' .. tostring(value) .. '"')
    return false
  end
  return true
end

local function validate_length(value, path)
  if type(value) ~= 'string' or not value:match(LEN_RE) then
    err(path .. ': expected length like "4pt" or "20mm", got "' .. tostring(value) .. '"')
    return false
  end
  return true
end

local function validate_number(value, path)
  if type(value) ~= 'string' or not value:match(NUM_RE) then
    err(path .. ': expected number like "1.25", got "' .. tostring(value) .. '"')
    return false
  end
  return true
end

local function validate_enum(value, allowed, path)
  for _, a in ipairs(allowed) do if value == a then return true end end
  err(path .. ': expected one of {' .. table.concat(allowed, ', ') ..
      '}, got "' .. tostring(value) .. '"')
  return false
end

local function require_path(t, path)
  local v = get_path(t, path)
  if v == nil then err(path .. ': required field is missing') return nil end
  return v
end

-- =============================================================================
-- Palette reference resolution — {{accent.primary}} → literal hex
-- =============================================================================

local function resolve_palette_refs(palette)
  if type(palette) ~= 'table' then return end

  local function resolve_one(s)
    if type(s) ~= 'string' or not s:find('{{') then return s end
    local out, _ = s:gsub('{{%s*([%w%._]+)%s*}}', function(path)
      local val = get_path(palette, path)
      if type(val) ~= 'string' then
        err('unresolved palette ref {{' .. path .. '}}')
        return '#000000'
      end
      return val
    end)
    return out
  end

  for _ = 1, 4 do
    local function walk(node)
      if type(node) ~= 'table' then return end
      for k, v in pairs(node) do
        if type(v) == 'string' then
          node[k] = resolve_one(v)
        elseif type(v) == 'table' then
          walk(v)
        end
      end
    end
    walk(palette)
  end
end

-- =============================================================================
-- Dial validation — checked before compute_defaults consumes them
-- =============================================================================

local function validate_dials(theme)
  require_path(theme, 'type.base')
  require_path(theme, 'type.scale')
  require_path(theme, 'rhythm.base')
  require_path(theme, 'fonts.main.family')
  require_path(theme, 'palette.page.bg')
  require_path(theme, 'palette.text.primary')

  local len_paths = {
    'type.base', 'rhythm.base',
    'page.margin.top', 'page.margin.bottom', 'page.margin.left', 'page.margin.right',
    'page.header.height', 'page.header.sep', 'page.footer.skip',
    'rules.thin', 'rules.thick', 'rules.callout_border',
    'list.indent', 'list.sub_indent',
    'image.placeholder_height',
  }
  for _, p in ipairs(len_paths) do
    local v = get_path(theme, p)
    if v ~= nil then validate_length(v, p) end
  end

  local num_paths = {
    'type.scale',
    'rhythm.heading.space', 'rhythm.heading.step', 'rhythm.heading.content_proximity',
    'rhythm.block.before',
    'rhythm.callout.after', 'rhythm.callout.pad_y', 'rhythm.callout.pad_x',
    'rhythm.code.after', 'rhythm.code.pad_x',
    'rhythm.table.after', 'rhythm.table.col_sep', 'rhythm.table.row_stretch',
    'rhythm.list.top_sep', 'rhythm.list.item_sep',
    'rhythm.image_placeholder.space',
    'rhythm.split.gutter',
    'rhythm.footnote.gap',
    'fonts.mono.scale', 'image.default_width',
  }
  for _, p in ipairs(num_paths) do
    local v = get_path(theme, p)
    if v ~= nil then validate_number(v, p) end
  end

  -- Per-role factors: size_exponents, size_factors, leading — all numbers.
  for _, group in ipairs({ 'size_exponents', 'size_factors', 'leading' }) do
    local tbl = (theme.type or {})[group] or {}
    for role, val in pairs(tbl) do
      validate_number(val, 'type.' .. group .. '.' .. role)
    end
  end

  local layout = theme.layout or {}
  if layout.cover and layout.cover.style then
    validate_enum(layout.cover.style,
      { 'centered-ascii', 'title-top', 'none' }, 'layout.cover.style')
  end
  if layout.header and layout.header.content then
    validate_enum(layout.header.content,
      { 'title-version', 'title-only', 'section', 'none' }, 'layout.header.content')
  end
  if layout.numbering and layout.numbering.scheme then
    validate_enum(layout.numbering.scheme,
      { 'arabic', 'none', 'roman' }, 'layout.numbering.scheme')
  end
  if layout.tables and layout.tables.break_threshold ~= nil then
    validate_number(layout.tables.break_threshold, 'layout.tables.break_threshold')
  end
end

-- =============================================================================
-- compute_defaults — read dials, produce the tokens tree
-- =============================================================================

local function compute_defaults(theme)
  local tokens = { type = {}, rhythm = {} }

  -- ---- Type ----------------------------------------------------------------
  -- All type math is data-driven: walk size_exponents / size_factors / leading
  -- from the YAML. Formulas live in the YAML; this code just multiplies.
  --
  --   heading size = base × scale^exponent    (for roles in size_exponents)
  --   other size   = base × factor            (for roles in size_factors)
  --   body         = base
  --   leading      = size × leading[role]     (per role)
  --
  -- Two identity defaults are hardcoded: cover_title inherits h1; toc_title
  -- inherits h2. Any role can override via the overrides: block.
  local base_pt, base_u = parse_length(theme.type.base)
  local scale   = tonumber(theme.type.scale) or 1.25
  local exps    = theme.type.size_exponents or {}
  local factors = theme.type.size_factors or {}
  local leading = theme.type.leading or {}

  local function S(n) return fmt_length(n, base_u) end

  local t = tokens.type

  -- Sizes
  t.body = S(base_pt)
  for role, exponent in pairs(exps) do
    t[role] = S(base_pt * scale ^ (tonumber(exponent) or 0))
  end
  for role, factor in pairs(factors) do
    t[role] = S(base_pt * (tonumber(factor) or 1.0))
  end
  -- Inherited identities
  t.cover_title = t.cover_title or t.h1
  t.toc_title   = t.toc_title   or t.h2

  -- Leading — walk the per-role leading table. Each role's line-height is
  -- its size × the role's leading factor. If a role has no leading defined,
  -- it falls back to body's leading factor.
  local body_lh_factor = tonumber(leading.body) or 1.5
  t.body_lh = S(base_pt * body_lh_factor)

  -- Collect role names first so we can safely iterate while adding keys.
  local size_roles = {}
  for role, _ in pairs(t) do
    if not role:match('_lh$') and role ~= 'body' then
      size_roles[#size_roles + 1] = role
    end
  end
  for _, role in ipairs(size_roles) do
    local size_pt = pt_of(t[role])
    if size_pt ~= nil then
      local factor = tonumber(leading[role]) or body_lh_factor
      t[role .. '_lh'] = S(size_pt * factor)
    end
  end

  -- ---- Rhythm --------------------------------------------------------------
  local r_pt, r_u = parse_length(theme.rhythm.base)
  local function R(n) return fmt_length(n, r_u) end

  local h      = theme.rhythm.heading or {}
  local space  = tonumber(h.space) or 7
  local step   = tonumber(h.step)  or 0.7
  local cprox  = tonumber(h.content_proximity) or 0.2
  local h1b = r_pt * space
  local h2b = h1b * step
  local h3b = h2b * step
  local h4b = h3b * step

  local r = tokens.rhythm
  r.unit = R(r_pt)
  r.xs   = R(r_pt * 0.5)
  r.sm   = R(r_pt * 1.0)
  r.md   = R(r_pt * 2.0)
  r.lg   = R(r_pt * 3.0)
  r.xl   = R(r_pt * 5.0)

  r.h1_before = R(h1b); r.h1_after = R(h1b * cprox)
  r.h2_before = R(h2b); r.h2_after = R(h2b * cprox)
  r.h3_before = R(h3b); r.h3_after = R(h3b * cprox)
  r.h4_before = R(h4b); r.h4_after = R(h4b * cprox)

  local b_before = tonumber((theme.rhythm.block or {}).before) or 2.5
  local co = theme.rhythm.callout or {}
  local cd = theme.rhythm.code or {}
  local tb = theme.rhythm.table or {}
  local ls = theme.rhythm.list or {}
  local ip = theme.rhythm.image_placeholder or {}
  local sp = theme.rhythm.split or {}
  local fn = theme.rhythm.footnote or {}

  r.callout_before = R(r_pt * b_before)
  r.callout_after  = R(r_pt * (tonumber(co.after) or 2.5))
  r.callout_pad_y  = R(r_pt * (tonumber(co.pad_y) or 2))
  r.callout_pad_x  = R(r_pt * (tonumber(co.pad_x) or 3))
  r.code_before    = R(r_pt * b_before)
  r.code_after     = R(r_pt * (tonumber(cd.after) or 3.5))
  r.code_pad_x     = R(r_pt * (tonumber(cd.pad_x) or 2.5))
  r.table_before   = R(r_pt * b_before)
  r.table_after    = R(r_pt * (tonumber(tb.after) or 3.5))
  r.table_col_sep  = R(r_pt * (tonumber(tb.col_sep) or 2))
  r.table_row_stretch    = tostring(tonumber(tb.row_stretch) or 1.45)
  r.list_top_sep         = R(r_pt * (tonumber(ls.top_sep) or 1.5))
  r.list_item_sep        = R(r_pt * (tonumber(ls.item_sep) or 1.25))
  r.image_placeholder_before = R(r_pt * (tonumber(ip.space) or 2))
  r.image_placeholder_after  = R(r_pt * (tonumber(ip.space) or 2))
  r.split_gutter             = R(r_pt * (tonumber(sp.gutter) or 4))
  r.footnote_gap             = R(r_pt * (tonumber(fn.gap) or 1))

  return tokens
end

-- =============================================================================
-- Override routing
-- type.*    → tokens.type.*
-- rhythm.*  → tokens.rhythm.*
-- palette.*, fonts.*, layout.*, page.*, rules.*, list.*, image.* → theme.*
-- =============================================================================

local TOKEN_ROOTS = { type = true, rhythm = true }
local THEME_ROOTS = {
  palette = true, fonts = true, layout = true,
  page = true, rules = true, list = true, image = true,
}

local function apply_overrides(theme, tokens, overrides)
  if overrides == nil or type(overrides) ~= 'table' then return end
  for k, v in pairs(overrides) do
    if type(k) == 'string' then
      local parts = split_path(k)
      local root = parts[1]
      table.remove(parts, 1)
      local value = v
      if type(v) == 'table' then value = utils.stringify(v) end
      if type(v) == 'number' then value = tostring(v) end

      if TOKEN_ROOTS[root] then
        set_path(tokens[root], parts, value)
      elseif THEME_ROOTS[root] then
        set_path(theme[root], parts, value)
      else
        err('unknown override path prefix: "' .. k .. '" (valid roots: type, rhythm, palette, fonts, layout, page, rules, list, image)')
      end
    end
  end
end

-- =============================================================================
-- Post-override validation
-- =============================================================================

local function validate_palette(theme)
  local hex_paths = {
    'palette.page.bg', 'palette.page.fg',
    'palette.surface.bg',
    'palette.code.bg',
    'palette.placeholder.bg', 'palette.placeholder.border',
    'palette.text.primary', 'palette.text.secondary', 'palette.text.tertiary',
    'palette.accent.primary', 'palette.accent.muted',
    'palette.rule.table',
    'palette.footnote.bg',
    'palette.callout.note.border',
    'palette.callout.tip.border',
    'palette.callout.warning.border',
    'palette.callout.important.border',
    'palette.syntax.string',
    'palette.syntax.comment',
    'palette.syntax.number',
  }
  for _, p in ipairs(hex_paths) do
    local v = get_path(theme, p)
    if v ~= nil then validate_hex(v, p) end
  end
end

-- =============================================================================
-- LaTeX emission
-- =============================================================================

local function emit_tokens(theme, tokens)
  local out = {}
  local function add(s) out[#out + 1] = s end
  local function len(name, value)
    add(string.format('\\newlength{\\%s}\\setlength{\\%s}{%s}', name, name, value))
  end

  add('% ===== Markset tokens (generated by apply-theme.lua) =====')

  -- Fonts (macros)
  local f = theme.fonts
  add(string.format('\\newcommand{\\msfontmain}{%s}', f.main.family))
  add(string.format('\\newcommand{\\msmainregular}{%s}',    f.main.weights.regular))
  add(string.format('\\newcommand{\\msmainbold}{%s}',       f.main.weights.bold))
  add(string.format('\\newcommand{\\msmainitalic}{%s}',     f.main.weights.italic))
  add(string.format('\\newcommand{\\msmainbolditalic}{%s}', f.main.weights.bolditalic))
  add(string.format('\\newcommand{\\msfontmono}{%s}', f.mono.family))
  add(string.format('\\newcommand{\\msmonoregular}{%s}',    f.mono.weights.regular))
  add(string.format('\\newcommand{\\msmonobold}{%s}',       f.mono.weights.bold))
  add(string.format('\\newcommand{\\msmonoitalic}{%s}',     f.mono.weights.italic))
  add(string.format('\\newcommand{\\msmonobolditalic}{%s}', f.mono.weights.bolditalic))
  add(string.format('\\newcommand{\\msmonoscale}{%s}', f.mono.scale))

  -- Spacing scale + rhythm unit
  local r = tokens.rhythm
  len('msunit',    r.unit)
  len('msspacexs', r.xs)
  len('msspacesm', r.sm)
  len('msspacemd', r.md)
  len('msspacelg', r.lg)
  len('msspacexl', r.xl)

  -- Type sizes + leading — LaTeX names cannot contain digits, so h1-h4 → hone/htwo/hthree/hfour
  local role_token = {
    body         = 'body',
    h1           = 'hone',
    h2           = 'htwo',
    h3           = 'hthree',
    h4           = 'hfour',
    caption      = 'caption',
    header       = 'header',
    code         = 'code',
    inline_code  = 'inlinecode',
    line_number  = 'linenumber',
    cover_title  = 'covertitle',
    cover_meta   = 'covermeta',
    ascii_cover  = 'asciicover',
    ascii_body   = 'asciibody',
    toc_title    = 'toctitle',
    toc_entry    = 'tocentry',
  }
  for role, token in pairs(role_token) do
    len('msfont' .. token,         tokens.type[role])
    len('msfont' .. token .. 'lh', tokens.type[role .. '_lh'])
  end

  -- Heading spacing
  len('mshonebefore',   r.h1_before);  len('mshoneafter',   r.h1_after)
  len('mshtwobefore',   r.h2_before);  len('mshtwoafter',   r.h2_after)
  len('mshthreebefore', r.h3_before);  len('mshthreeafter', r.h3_after)
  len('mshfourbefore',  r.h4_before);  len('mshfourafter',  r.h4_after)

  -- Block spacing
  len('mscalloutbefore', r.callout_before)
  len('mscalloutafter',  r.callout_after)
  len('mscalloutpady',   r.callout_pad_y)
  len('mscalloutpadx',   r.callout_pad_x)
  len('mscodebefore',    r.code_before)
  len('mscodeafter',     r.code_after)
  len('mscodepadx',      r.code_pad_x)
  len('mstablebefore',   r.table_before)
  len('mstableafter',    r.table_after)

  -- Tables
  len('mstablecolsep', r.table_col_sep)
  add(string.format('\\newcommand{\\mstablestretch}{%s}', r.table_row_stretch))

  -- Lists
  len('mslistindent',    theme.list.indent)
  len('mslistsubindent', theme.list.sub_indent)
  len('mslistitemsep',   r.list_item_sep)
  len('mslisttopsep',    r.list_top_sep)
  add(string.format('\\newcommand{\\mslistmarkerone}{%s}', theme.list.marker_l1))
  add(string.format('\\newcommand{\\mslistmarkertwo}{%s}', theme.list.marker_l2))

  -- Rules
  len('msrulethin',      theme.rules.thin)
  len('msrulethick',     theme.rules.thick)
  len('mscalloutborder', theme.rules.callout_border)

  -- Image
  add(string.format('\\newcommand{\\msimagedefaultwidth}{%s}', theme.image.default_width))
  len('msimageplaceholderheight', theme.image.placeholder_height)

  -- Split layouts
  len('msgutter', r.split_gutter)

  -- Footnote pill gap
  len('msfootgap', r.footnote_gap)

  -- Callout glyphs
  local cp = theme.palette.callout
  add(string.format('\\newcommand{\\msglyphnote}{%s}',      cp.note.glyph))
  add(string.format('\\newcommand{\\msglyphtip}{%s}',       cp.tip.glyph))
  add(string.format('\\newcommand{\\msglyphwarning}{%s}',   cp.warning.glyph))
  add(string.format('\\newcommand{\\msglyphimportant}{%s}', cp.important.glyph))

  -- Colours (header-includes injected AFTER \usepackage{xcolor})
  local function color(name, path)
    local hex = get_path(theme, path)
    add(string.format('\\definecolor{%s}{HTML}{%s}', name, hex_body(hex)))
  end
  color('pagebg',             'palette.page.bg')
  color('pagefg',             'palette.page.fg')
  color('surfacebg',          'palette.surface.bg')
  color('codebg',             'palette.code.bg')
  color('calloutbg',          'palette.surface.bg')
  color('placeholderbg',      'palette.placeholder.bg')
  color('placeholderborder',  'palette.placeholder.border')
  color('textprimary',        'palette.text.primary')
  color('textsecondary',      'palette.text.secondary')
  color('texttertiary',       'palette.text.tertiary')
  color('accentprimary',      'palette.accent.primary')
  color('accentmuted',        'palette.accent.muted')
  color('ruletable',          'palette.rule.table')
  color('footnotebg',         'palette.footnote.bg')
  color('noteborder',         'palette.callout.note.border')
  color('tipborder',          'palette.callout.tip.border')
  color('warningborder',      'palette.callout.warning.border')
  color('importantborder',    'palette.callout.important.border')
  color('synstring',          'palette.syntax.string')
  color('syncomment',         'palette.syntax.comment')
  color('synnumber',          'palette.syntax.number')

  -- Legacy aliases for any downstream code still using old names
  add('\\colorlet{bodytext}{textprimary}')
  add('\\colorlet{secondarytext}{textsecondary}')
  add('\\colorlet{tertiarytext}{texttertiary}')
  add('\\colorlet{secondary}{accentprimary}')
  add('\\colorlet{tablerule}{ruletable}')

  return table.concat(out, '\n')
end

-- =============================================================================
-- Main entry
-- =============================================================================

function Meta(meta)
  local theme = to_plain(meta.theme)
  if theme == nil then
    error('markset: no theme found. Pass one via --metadata-file or ./theme.yaml.')
  end

  -- Validate dials before consuming them
  validate_dials(theme)
  fail_if_errors()

  -- Compute the tokens tree from the dials
  local tokens = compute_defaults(theme)

  -- Apply overrides: theme-level first, then per-document frontmatter
  apply_overrides(theme, tokens, theme.overrides)
  apply_overrides(theme, tokens, to_plain(meta.theme_overrides))

  -- Resolve palette refs, then validate hex
  resolve_palette_refs(theme.palette)
  validate_palette(theme)
  fail_if_errors()

  -- Emit LaTeX
  local latex = emit_tokens(theme, tokens)
  local block = pandoc.RawBlock('latex', latex)
  local existing = meta['header-includes']
  if existing == nil then
    meta['header-includes'] = pandoc.MetaBlocks({ block })
  elseif existing.t == 'MetaList' then
    table.insert(existing, pandoc.MetaBlocks({ block }))
    meta['header-includes'] = existing
  else
    meta['header-includes'] = pandoc.MetaList({
      pandoc.MetaBlocks({ block }),
      existing,
    })
  end

  -- Layout boolean flags for template $if(...)$
  local layout = theme.layout or {}
  local cover_style = (layout.cover and layout.cover.style) or 'centered-ascii'
  local header_mode = (layout.header and layout.header.content) or 'title-version'
  local toc_include = true
  if layout.toc and layout.toc.include == false then toc_include = false end
  local num_scheme  = (layout.numbering and layout.numbering.scheme) or 'arabic'
  local h1_numbered = (layout.numbering and layout.numbering.h1_numbered) or false

  local function flag(name, val) meta[name] = pandoc.MetaBool(val and true or false) end
  flag('ms_cover_centered_ascii', cover_style == 'centered-ascii')
  flag('ms_cover_title_top',      cover_style == 'title-top')
  flag('ms_cover_none',           cover_style == 'none')
  flag('ms_header_title_version', header_mode == 'title-version')
  flag('ms_header_title_only',    header_mode == 'title-only')
  flag('ms_header_section',       header_mode == 'section')
  flag('ms_header_none',          header_mode == 'none')
  flag('ms_toc_include',          toc_include)
  flag('ms_numbering_arabic',     num_scheme == 'arabic')
  flag('ms_numbering_roman',      num_scheme == 'roman')
  flag('ms_numbering_none',       num_scheme == 'none')
  flag('ms_h1_numbered',          h1_numbered == true)

  -- Table break threshold — consumed by divs.lua, not the template
  local tables_cfg = layout.tables or {}
  local break_threshold = tonumber(tables_cfg.break_threshold) or 12
  meta.ms_table_break_threshold = pandoc.MetaString(tostring(break_threshold))

  -- Geometry strings exposed as top-level template vars
  local function mstr(name, val) meta[name] = pandoc.MetaString(val) end
  mstr('mspage_margin_top',    theme.page.margin.top)
  mstr('mspage_margin_bottom', theme.page.margin.bottom)
  mstr('mspage_margin_left',   theme.page.margin.left)
  mstr('mspage_margin_right',  theme.page.margin.right)
  mstr('mspage_header_height', theme.page.header.height)
  mstr('mspage_header_sep',    theme.page.header.sep)
  mstr('mspage_footer_skip',   theme.page.footer.skip)

  return meta
end
