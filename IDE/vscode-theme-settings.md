# VS Code Theme Settings

Paste the following into your VS Code `settings.json` (`Cmd+Shift+P` → "Open User Settings (JSON)").

```json
{
  "workbench.colorCustomizations": {
    "editor.background": "#0c0a10",
    "editor.foreground": "#d0cdd8",
    "editor.lineHighlightBackground": "#120f1c",
    "editor.selectionBackground": "#7b6a9e40",
    "editor.selectionHighlightBackground": "#7b6a9e22",
    "editor.wordHighlightBackground": "#7b6a9e22",
    "editor.wordHighlightStrongBackground": "#7b6a9e33",
    "editor.findMatchBackground": "#7b6a9e88",
    "editor.findMatchHighlightBackground": "#7b6a9e55",
    "editor.findRangeHighlightBackground": "#7b6a9e22",

    "editorCursor.foreground": "#7b6a9e",
    "editorLineNumber.foreground": "#4a4553",
    "editorLineNumber.activeForeground": "#8a8494",
    "editorIndentGuide.background1": "#1a1622",
    "editorIndentGuide.activeBackground1": "#2a2435",
    "editorBracketMatch.background": "#7b6a9e33",
    "editorBracketMatch.border": "#7b6a9e88",

    "editorWidget.background": "#0e0c14",
    "editorWidget.border": "#2a2435",
    "editorSuggestWidget.background": "#0e0c14",
    "editorSuggestWidget.border": "#2a2435",
    "editorSuggestWidget.selectedBackground": "#7b6a9e33",
    "editorHoverWidget.background": "#0e0c14",
    "editorHoverWidget.border": "#2a2435",

    "sideBar.background": "#0a0810",
    "sideBar.foreground": "#8a8494",
    "sideBar.border": "#2a2435",
    "sideBarTitle.foreground": "#b5afc0",
    "sideBarSectionHeader.background": "#0a0810",
    "sideBarSectionHeader.foreground": "#b5afc0",
    "sideBarSectionHeader.border": "#2a2435",

    "list.activeSelectionBackground": "#7b6a9e33",
    "list.activeSelectionForeground": "#d0cdd8",
    "list.inactiveSelectionBackground": "#7b6a9e22",
    "list.hoverBackground": "#7b6a9e18",
    "list.focusBackground": "#7b6a9e33",

    "activityBar.background": "#08070e",
    "activityBar.foreground": "#d0cdd8",
    "activityBar.inactiveForeground": "#5c5668",
    "activityBar.border": "#2a2435",
    "activityBar.activeBorder": "#7b6a9e",
    "activityBarBadge.background": "#7b6a9e",
    "activityBarBadge.foreground": "#0c0a10",

    "titleBar.activeBackground": "#08070e",
    "titleBar.activeForeground": "#8a8494",
    "titleBar.inactiveBackground": "#08070e",
    "titleBar.inactiveForeground": "#6a6378",
    "titleBar.border": "#2a2435",

    "tab.activeBackground": "#0c0a10",
    "tab.activeForeground": "#d0cdd8",
    "tab.activeBorderTop": "#7b6a9e",
    "tab.inactiveBackground": "#08070e",
    "tab.inactiveForeground": "#6a6378",
    "tab.border": "#2a2435",
    "editorGroupHeader.tabsBackground": "#08070e",
    "editorGroupHeader.tabsBorder": "#2a2435",
    "editorGroup.border": "#2a2435",

    "panel.background": "#000000",
    "panel.border": "#2a2435",
    "panelTitle.activeBorder": "#7b6a9e",
    "panelTitle.activeForeground": "#d0cdd8",
    "panelTitle.inactiveForeground": "#5c5668",

    "terminal.background": "#000000",
    "terminal.foreground": "#d0cdd8",
    "terminal.ansiBlack": "#0c0a10",
    "terminal.ansiRed": "#d4a0b9",
    "terminal.ansiGreen": "#a3bf8f",
    "terminal.ansiYellow": "#d4c78f",
    "terminal.ansiBlue": "#8fadcc",
    "terminal.ansiMagenta": "#b0a0d4",
    "terminal.ansiCyan": "#8dc0b5",
    "terminal.ansiWhite": "#ccc8d4",
    "terminal.ansiBrightBlack": "#5c5668",
    "terminal.ansiBrightRed": "#e0b0c6",
    "terminal.ansiBrightGreen": "#b5d1a0",
    "terminal.ansiBrightYellow": "#e0d4a0",
    "terminal.ansiBrightBlue": "#a3c0db",
    "terminal.ansiBrightMagenta": "#c4b4e0",
    "terminal.ansiBrightCyan": "#a0d4c8",
    "terminal.ansiBrightWhite": "#d8d5e0",

    "statusBar.background": "#08070e",
    "statusBar.foreground": "#6a6378",
    "statusBar.border": "#2a2435",
    "statusBar.debuggingBackground": "#08070e",
    "statusBar.noFolderBackground": "#08070e",

    "input.background": "#110f18",
    "input.border": "#2a2435",
    "input.foreground": "#d0cdd8",
    "input.placeholderForeground": "#5c5668",
    "focusBorder": "#7b6a9e",

    "dropdown.background": "#0e0c14",
    "dropdown.border": "#2a2435",
    "dropdown.foreground": "#d0cdd8",

    "button.background": "#7b6a9e",
    "button.foreground": "#0c0a10",
    "button.hoverBackground": "#8a79ad",

    "scrollbarSlider.background": "#7b6a9e22",
    "scrollbarSlider.hoverBackground": "#7b6a9e44",
    "scrollbarSlider.activeBackground": "#7b6a9e66",

    "minimap.background": "#0c0a10",
    "minimapSlider.background": "#7b6a9e22",

    "breadcrumb.foreground": "#6a6378",
    "breadcrumb.focusForeground": "#d0cdd8",
    "breadcrumb.activeSelectionForeground": "#d0cdd8",

    "peekView.border": "#2a2435",
    "peekViewEditor.background": "#0c0a10",
    "peekViewResult.background": "#0a0810",
    "peekViewTitle.background": "#0a0810",

    "gitDecoration.modifiedResourceForeground": "#8fadcc",
    "gitDecoration.untrackedResourceForeground": "#a3bf8f",
    "gitDecoration.deletedResourceForeground": "#d4a0b9",
    "gitDecoration.ignoredResourceForeground": "#5c566888",
    "gitDecoration.addedResourceForeground": "#a3bf8f",
    "gitDecoration.stageModifiedResourceForeground": "#a3c0db",
    "gitDecoration.stageDeletedResourceForeground": "#e0b0c6",
    "gitDecoration.conflictingResourceForeground": "#d4c78f",
    "gitDecoration.submoduleResourceForeground": "#b0a0d4",
    "gitDecoration.renamedResourceForeground": "#8dc0b5",
    "editorGutter.addedBackground": "#a3bf8f88",
    "editorGutter.modifiedBackground": "#8fadcc88",
    "editorGutter.deletedBackground": "#d4a0b988",
    "editorGutter.commentRangeForeground": "#5c5668",
    "editorGutter.foldingControlForeground": "#8a8494",

    "diffEditor.insertedTextBackground": "#a3bf8f22",
    "diffEditor.removedTextBackground": "#d4a0b922",
    "diffEditor.insertedLineBackground": "#a3bf8f10",
    "diffEditor.removedLineBackground": "#d4a0b910",
    "diffEditor.diagonalFill": "#2a243533",
    "diffEditorGutter.insertedLineBackground": "#a3bf8f40",
    "diffEditorGutter.removedLineBackground": "#d4a0b940",
    "diffEditorOverview.insertedForeground": "#a3bf8f66",
    "diffEditorOverview.removedForeground": "#d4a0b966",

    "search.resultsInfoForeground": "#8a8494",
    "searchEditor.findMatchBackground": "#7b6a9e33",
    "searchEditor.findMatchBorder": "#7b6a9e66",

    "editorError.foreground": "#e27d9c",
    "editorWarning.foreground": "#d4c78f",
    "editorInfo.foreground": "#8fadcc",
    "editorHint.foreground": "#8dc0b5",
    "editorOverviewRuler.errorForeground": "#e27d9c",
    "problemsErrorIcon.foreground": "#e27d9c",
    "problemsWarningIcon.foreground": "#d4c78f",
    "problemsInfoIcon.foreground": "#8fadcc",

    "editorBracketHighlight.foreground1": "#b0a0d4",
    "editorBracketHighlight.foreground2": "#8dc0b5",
    "editorBracketHighlight.foreground3": "#d4a888",
    "editorBracketHighlight.foreground4": "#8fadcc",
    "editorBracketHighlight.foreground5": "#b0a0d4",
    "editorBracketHighlight.foreground6": "#8dc0b5",
    "editorBracketHighlight.unexpectedBracket.foreground": "#e27d9c",

    "debugToolBar.background": "#0e0c14",
    "debugToolBar.border": "#2a2435",
    "editor.stackFrameHighlightBackground": "#d4c78f15",
    "editor.focusedStackFrameHighlightBackground": "#a3bf8f15",
    "debugIcon.breakpointForeground": "#d4a0b9",
    "debugIcon.breakpointDisabledForeground": "#5c5668",
    "debugIcon.startForeground": "#a3bf8f",
    "debugIcon.pauseForeground": "#d4c78f",
    "debugIcon.stopForeground": "#e27d9c",
    "debugIcon.stepOverForeground": "#8fadcc",
    "debugIcon.stepIntoForeground": "#8fadcc",
    "debugIcon.stepOutForeground": "#8fadcc",
    "debugIcon.restartForeground": "#a3bf8f",
    "debugConsole.infoForeground": "#8fadcc",
    "debugConsole.warningForeground": "#d4c78f",
    "debugConsole.errorForeground": "#e27d9c",
    "debugConsole.sourceForeground": "#8a8494",
    "debugTokenExpression.name": "#8dc0b5",
    "debugTokenExpression.value": "#d4a0b9",
    "debugTokenExpression.string": "#d4a0b9",
    "debugTokenExpression.boolean": "#d4c78f",
    "debugTokenExpression.number": "#d4c78f",

    "notificationCenter.border": "#2a2435",
    "notificationCenterHeader.background": "#0e0c14",
    "notificationCenterHeader.foreground": "#d0cdd8",
    "notifications.background": "#0e0c14",
    "notifications.foreground": "#d0cdd8",
    "notifications.border": "#2a2435",
    "notificationLink.foreground": "#8fadcc",
    "notificationsErrorIcon.foreground": "#e27d9c",
    "notificationsWarningIcon.foreground": "#d4c78f",
    "notificationsInfoIcon.foreground": "#8fadcc",
    "notificationToast.border": "#2a2435",

    "quickInput.background": "#0e0c14",
    "quickInput.foreground": "#d0cdd8",
    "quickInputList.focusBackground": "#7b6a9e33",
    "quickInputList.focusForeground": "#d0cdd8",
    "quickInputList.focusIconForeground": "#d0cdd8",
    "quickInputTitle.background": "#0e0c14",
    "pickerGroup.border": "#2a2435",
    "pickerGroup.foreground": "#7b6a9e",
    "keybindingLabel.background": "#1e1a2a",
    "keybindingLabel.foreground": "#d0cdd8",
    "keybindingLabel.border": "#2a2435",
    "keybindingLabel.bottomBorder": "#2a2435",

    "merge.currentHeaderBackground": "#a3bf8f33",
    "merge.currentContentBackground": "#a3bf8f15",
    "merge.incomingHeaderBackground": "#8fadcc33",
    "merge.incomingContentBackground": "#8fadcc15",
    "merge.commonHeaderBackground": "#d4c78f33",
    "merge.commonContentBackground": "#d4c78f15",
    "merge.border": "#2a2435",
    "editorOverviewRuler.currentContentForeground": "#a3bf8f66",
    "editorOverviewRuler.incomingContentForeground": "#8fadcc66",
    "editorOverviewRuler.commonContentForeground": "#d4c78f66",

    "editorRuler.foreground": "#1e1a2a",
    "editorCodeLens.foreground": "#5c5668",
    "editorLightBulb.foreground": "#d4c78f",
    "editorLightBulbAutoFix.foreground": "#a3bf8f",

    "editorInlayHint.background": "#1a162266",
    "editorInlayHint.foreground": "#8a8494",
    "editorInlayHint.typeBackground": "#1a162266",
    "editorInlayHint.typeForeground": "#8a8494",
    "editorInlayHint.parameterBackground": "#1a162266",
    "editorInlayHint.parameterForeground": "#8a8494",

    "menu.background": "#0e0c14",
    "menu.foreground": "#d0cdd8",
    "menu.selectionBackground": "#7b6a9e33",
    "menu.selectionForeground": "#d0cdd8",
    "menu.separatorBackground": "#2a2435",
    "menu.border": "#2a2435",
    "menubar.selectionBackground": "#7b6a9e33",
    "menubar.selectionForeground": "#d0cdd8",

    "testing.iconPassed": "#a3bf8f",
    "testing.iconFailed": "#e27d9c",
    "testing.iconErrored": "#e0b0c6",
    "testing.iconSkipped": "#d4c78f",
    "testing.iconQueued": "#8fadcc",
    "testing.runAction": "#a3bf8f",
    "testing.message.error.decorationForeground": "#e27d9c",
    "testing.message.error.lineBackground": "#e27d9c18",
    "testing.message.info.decorationForeground": "#8fadcc",

    "symbolIcon.arrayForeground": "#d4a888",
    "symbolIcon.booleanForeground": "#d4c78f",
    "symbolIcon.classForeground": "#8fadcc",
    "symbolIcon.colorForeground": "#a58fb5",
    "symbolIcon.constantForeground": "#d4c78f",
    "symbolIcon.constructorForeground": "#b0a0d4",
    "symbolIcon.enumeratorForeground": "#d4a888",
    "symbolIcon.enumeratorMemberForeground": "#d4c78f",
    "symbolIcon.eventForeground": "#d4a888",
    "symbolIcon.fieldForeground": "#a3bf8f",
    "symbolIcon.fileForeground": "#8a8494",
    "symbolIcon.folderForeground": "#8a8494",
    "symbolIcon.functionForeground": "#8dc0b5",
    "symbolIcon.interfaceForeground": "#8fadcc",
    "symbolIcon.keyForeground": "#d4a888",
    "symbolIcon.keywordForeground": "#b0a0d4",
    "symbolIcon.methodForeground": "#8dc0b5",
    "symbolIcon.moduleForeground": "#8a8494",
    "symbolIcon.namespaceForeground": "#b0a0d4",
    "symbolIcon.nullForeground": "#d4c78f",
    "symbolIcon.numberForeground": "#d4c78f",
    "symbolIcon.objectForeground": "#d4a888",
    "symbolIcon.operatorForeground": "#8a8494",
    "symbolIcon.packageForeground": "#b0a0d4",
    "symbolIcon.propertyForeground": "#d4a888",
    "symbolIcon.referenceForeground": "#8fadcc",
    "symbolIcon.snippetForeground": "#8dc0b5",
    "symbolIcon.stringForeground": "#d4a0b9",
    "symbolIcon.structForeground": "#8fadcc",
    "symbolIcon.textForeground": "#8a8494",
    "symbolIcon.typeParameterForeground": "#8fadcc",
    "symbolIcon.unitForeground": "#d4c78f",
    "symbolIcon.variableForeground": "#a3bf8f"
  },

  "editor.tokenColorCustomizations": {
    "comments": "#6a6378",
    "textMateRules": [
      {
        "scope": ["comment", "punctuation.definition.comment"],
        "settings": { "foreground": "#6a6378", "fontStyle": "italic" }
      },
      {
        "scope": ["keyword", "keyword.control", "storage.type", "storage.modifier"],
        "settings": { "foreground": "#b0a0d4" }
      },
      {
        "scope": ["string", "string.quoted", "string.template"],
        "settings": { "foreground": "#d4a0b9" }
      },
      {
        "scope": ["entity.name.function", "support.function", "meta.function-call"],
        "settings": { "foreground": "#8dc0b5" }
      },
      {
        "scope": ["entity.name.type", "support.type", "support.class", "entity.name.class"],
        "settings": { "foreground": "#8fadcc" }
      },
      {
        "scope": ["variable", "variable.other", "variable.parameter"],
        "settings": { "foreground": "#a3bf8f" }
      },
      {
        "scope": ["constant.numeric", "constant.language"],
        "settings": { "foreground": "#d4c78f" }
      },
      {
        "scope": ["entity.name.tag", "support.type.property-name"],
        "settings": { "foreground": "#d4a888" }
      },
      {
        "scope": ["keyword.operator", "punctuation.accessor"],
        "settings": { "foreground": "#8a8494" }
      },
      {
        "scope": ["punctuation", "meta.brace", "punctuation.definition.block"],
        "settings": { "foreground": "#8a8494" }
      },
      {
        "scope": ["variable.other.constant", "variable.other.enummember"],
        "settings": { "foreground": "#d4c78f" }
      },
      {
        "scope": ["entity.other.attribute-name"],
        "settings": { "foreground": "#a3bf8f" }
      },
      {
        "scope": ["keyword.control.import", "keyword.control.from", "keyword.control.export"],
        "settings": { "foreground": "#b0a0d4" }
      },
      {
        "scope": ["support.type.primitive"],
        "settings": { "foreground": "#8fadcc" }
      },
      {
        "name": "Language variables (this, self, super)",
        "scope": ["variable.language", "variable.language.this", "variable.language.self", "variable.language.super"],
        "settings": { "foreground": "#c4a0c4" }
      },
      {
        "name": "Decorators",
        "scope": [
          "meta.decorator",
          "meta.decorator entity.name.function",
          "punctuation.decorator",
          "tag.decorator"
        ],
        "settings": { "foreground": "#d4a888" }
      },
      {
        "name": "Template literal expression delimiters",
        "scope": [
          "punctuation.definition.template-expression.begin",
          "punctuation.definition.template-expression.end",
          "punctuation.section.embedded"
        ],
        "settings": { "foreground": "#c4a0c4" }
      },
      {
        "name": "String escape sequences",
        "scope": ["constant.character.escape", "constant.character.escape.backslash"],
        "settings": { "foreground": "#c4a0c4" }
      },
      {
        "name": "Deprecated",
        "scope": ["invalid.deprecated", "entity.name.function.deprecated"],
        "settings": { "foreground": "#8a8494", "fontStyle": "strikethrough" }
      },
      {
        "name": "Invalid / illegal",
        "scope": ["invalid", "invalid.illegal"],
        "settings": { "foreground": "#e0b0c6" }
      },
      {
        "name": "Regex literal",
        "scope": ["string.regexp"],
        "settings": { "foreground": "#d4a0b9" }
      },
      {
        "name": "Regex group punctuation",
        "scope": [
          "punctuation.definition.group.regexp",
          "punctuation.definition.group.assertion.regexp",
          "punctuation.definition.character-class.regexp"
        ],
        "settings": { "foreground": "#8a8494" }
      },
      {
        "name": "Regex quantifiers and anchors",
        "scope": [
          "keyword.operator.quantifier.regexp",
          "keyword.control.anchor.regexp",
          "keyword.other.back-reference.regexp"
        ],
        "settings": { "foreground": "#c4a0c4" }
      },
      {
        "name": "Regex character classes and escapes",
        "scope": [
          "constant.other.character-class.regexp",
          "constant.other.character-class.set.regexp",
          "constant.character.character-class.regexp",
          "constant.character.escape.regexp"
        ],
        "settings": { "foreground": "#d4c78f" }
      },
      {
        "name": "JSX / TSX tag punctuation",
        "scope": [
          "punctuation.definition.tag.begin.tsx",
          "punctuation.definition.tag.end.tsx",
          "punctuation.definition.tag.begin.jsx",
          "punctuation.definition.tag.end.jsx",
          "JSXElement.punctuation"
        ],
        "settings": { "foreground": "#8a8494" }
      },
      {
        "name": "JSX / TSX component names",
        "scope": [
          "support.class.component",
          "support.class.component.jsx",
          "support.class.component.tsx"
        ],
        "settings": { "foreground": "#8fadcc" }
      },
      {
        "name": "JSDoc / docstring tags",
        "scope": [
          "storage.type.class.jsdoc",
          "punctuation.definition.block.tag.jsdoc",
          "storage.type.class.phpdoc"
        ],
        "settings": { "foreground": "#b0a0d4", "fontStyle": "italic" }
      },
      {
        "name": "JSDoc types",
        "scope": [
          "entity.name.type.instance.jsdoc",
          "constant.language.access-type.jsdoc"
        ],
        "settings": { "foreground": "#8fadcc", "fontStyle": "italic" }
      },
      {
        "name": "JSDoc variable names",
        "scope": [
          "variable.other.jsdoc",
          "markup.underline.link.jsdoc"
        ],
        "settings": { "foreground": "#a3bf8f", "fontStyle": "italic" }
      },
      {
        "name": "Documentation comments",
        "scope": ["comment.block.documentation"],
        "settings": { "foreground": "#7a7484", "fontStyle": "italic" }
      },

      {
        "name": "Markdown H1",
        "scope": ["heading.1.markdown entity.name.section.markdown"],
        "settings": { "foreground": "#d4a0b9", "fontStyle": "bold" }
      },
      {
        "name": "Markdown H2",
        "scope": ["heading.2.markdown entity.name.section.markdown"],
        "settings": { "foreground": "#b0a0d4", "fontStyle": "bold" }
      },
      {
        "name": "Markdown H3",
        "scope": ["heading.3.markdown entity.name.section.markdown"],
        "settings": { "foreground": "#8fadcc", "fontStyle": "bold" }
      },
      {
        "name": "Markdown H4",
        "scope": ["heading.4.markdown entity.name.section.markdown"],
        "settings": { "foreground": "#8dc0b5", "fontStyle": "bold" }
      },
      {
        "name": "Markdown H5",
        "scope": ["heading.5.markdown entity.name.section.markdown"],
        "settings": { "foreground": "#d4c78f", "fontStyle": "bold" }
      },
      {
        "name": "Markdown H6",
        "scope": ["heading.6.markdown entity.name.section.markdown"],
        "settings": { "foreground": "#a3bf8f", "fontStyle": "bold" }
      },
      {
        "name": "Markdown heading hash marks",
        "scope": ["punctuation.definition.heading.markdown"],
        "settings": { "foreground": "#5c5668" }
      },
      {
        "name": "Markdown bold",
        "scope": ["markup.bold.markdown", "markup.bold"],
        "settings": { "foreground": "#d0cdd8", "fontStyle": "bold" }
      },
      {
        "name": "Markdown italic",
        "scope": ["markup.italic.markdown"],
        "settings": { "foreground": "#d0cdd8", "fontStyle": "italic" }
      },
      {
        "name": "Markdown bold italic",
        "scope": [
          "markup.bold.markdown markup.italic.markdown",
          "markup.italic.markdown markup.bold.markdown",
          "markup.bold_italic.markdown"
        ],
        "settings": { "foreground": "#d0cdd8", "fontStyle": "bold italic" }
      },
      {
        "name": "Markdown strikethrough",
        "scope": ["markup.strikethrough.markdown"],
        "settings": { "foreground": "#5c5668", "fontStyle": "strikethrough" }
      },
      {
        "name": "Markdown bold/italic/strikethrough markers",
        "scope": [
          "punctuation.definition.bold.markdown",
          "punctuation.definition.italic.markdown",
          "punctuation.definition.strikethrough.markdown"
        ],
        "settings": { "foreground": "#5c5668" }
      },
      {
        "name": "Markdown inline code",
        "scope": ["markup.inline.raw.string.markdown"],
        "settings": { "foreground": "#d4a0b9" }
      },
      {
        "name": "Markdown inline code backticks",
        "scope": ["punctuation.definition.raw.markdown"],
        "settings": { "foreground": "#5c5668" }
      },
      {
        "name": "Markdown escape characters",
        "scope": ["constant.character.escape.markdown"],
        "settings": { "foreground": "#c4a0c4" }
      },
      {
        "name": "Markdown fenced code block delimiters",
        "scope": ["punctuation.definition.markdown", "markup.fenced_code.block.markdown punctuation.definition.markdown"],
        "settings": { "foreground": "#5c5668" }
      },
      {
        "name": "Markdown fenced code language",
        "scope": ["fenced_code.block.language.markdown"],
        "settings": { "foreground": "#8dc0b5" }
      },
      {
        "name": "Markdown link text",
        "scope": ["string.other.link.title.markdown", "string.other.link.description.markdown"],
        "settings": { "foreground": "#8fadcc" }
      },
      {
        "name": "Markdown link URL",
        "scope": ["markup.underline.link.markdown", "markup.underline.link.image.markdown"],
        "settings": { "foreground": "#8dc0b5" }
      },
      {
        "name": "Markdown link brackets/parens",
        "scope": [
          "punctuation.definition.string.begin.markdown",
          "punctuation.definition.string.end.markdown",
          "punctuation.definition.metadata.markdown"
        ],
        "settings": { "foreground": "#8a8494" }
      },
      {
        "name": "Markdown image bang",
        "scope": ["punctuation.definition.link.description.begin.markdown"],
        "settings": { "foreground": "#d4a888" }
      },
      {
        "name": "Markdown blockquote",
        "scope": ["markup.quote.markdown"],
        "settings": { "foreground": "#6a6378", "fontStyle": "italic" }
      },
      {
        "name": "Markdown blockquote marker",
        "scope": ["punctuation.definition.quote.begin.markdown"],
        "settings": { "foreground": "#a3bf8f" }
      },
      {
        "name": "Markdown GFM alert label ([!NOTE], [!WARNING], etc.)",
        "scope": [
          "markup.quote.markdown markup.bold.markdown",
          "markup.quote.markdown entity.name.tag",
          "markup.alert.markdown",
          "markup.alert.note.markdown",
          "markup.alert.tip.markdown",
          "markup.alert.important.markdown",
          "markup.alert.warning.markdown",
          "markup.alert.caution.markdown"
        ],
        "settings": { "foreground": "#d4a888", "fontStyle": "bold" }
      },
      {
        "name": "Markdown list marker",
        "scope": ["punctuation.definition.list.begin.markdown", "markup.list.numbered.markdown punctuation.definition.list.begin.markdown"],
        "settings": { "foreground": "#d4a888" }
      },
      {
        "name": "Markdown horizontal rule",
        "scope": ["meta.separator.markdown"],
        "settings": { "foreground": "#5c5668" }
      },
      {
        "name": "Markdown raw/HTML tags",
        "scope": ["meta.tag.metadata.markdown", "text.html.markdown meta.tag"],
        "settings": { "foreground": "#d4a888" }
      },
      {
        "name": "Markdown HTML attributes",
        "scope": ["text.html.markdown entity.other.attribute-name"],
        "settings": { "foreground": "#a3bf8f" }
      },
      {
        "name": "Markdown HTML attribute values",
        "scope": ["text.html.markdown string.quoted"],
        "settings": { "foreground": "#d4a0b9" }
      },
      {
        "name": "Markdown table pipes",
        "scope": [
          "markup.table.markdown punctuation.definition.table.markdown",
          "punctuation.separator.table.markdown"
        ],
        "settings": { "foreground": "#8a8494" }
      },
      {
        "name": "Markdown table header separator",
        "scope": [
          "punctuation.separator.markdown",
          "markup.table.markdown meta.separator"
        ],
        "settings": { "foreground": "#5c5668" }
      },
      {
        "name": "Markdown task list checkbox brackets",
        "scope": [
          "markup.list.unnumbered.markdown punctuation.definition.list.markdown",
          "meta.paragraph.list.markdown punctuation.definition.string.markdown",
          "markup.checkbox.markdown"
        ],
        "settings": { "foreground": "#d4a888" }
      },
      {
        "name": "Markdown reference link definition label",
        "scope": [
          "meta.link.reference.def.markdown constant.other.reference.link.markdown",
          "meta.link.reference.def.markdown string.other.link.title.markdown"
        ],
        "settings": { "foreground": "#a3bf8f" }
      },
      {
        "name": "Markdown footnote reference",
        "scope": [
          "meta.link.reference.footnote.markdown",
          "markup.footnote.markdown",
          "constant.other.footnote.link.markdown"
        ],
        "settings": { "foreground": "#8fadcc" }
      },
      {
        "name": "Markdown YAML frontmatter fence",
        "scope": [
          "markup.raw.yaml.markdown punctuation.definition.markdown",
          "meta.embedded.block.frontmatter punctuation.definition"
        ],
        "settings": { "foreground": "#5c5668" }
      },
      {
        "name": "YAML frontmatter keys",
        "scope": [
          "markup.raw.yaml.markdown entity.name.tag.yaml",
          "meta.embedded.block.frontmatter entity.name.tag"
        ],
        "settings": { "foreground": "#d4a888" }
      },
      {
        "name": "YAML frontmatter string values",
        "scope": [
          "markup.raw.yaml.markdown string",
          "meta.embedded.block.frontmatter string"
        ],
        "settings": { "foreground": "#d4a0b9" }
      },
      {
        "name": "YAML frontmatter constants",
        "scope": [
          "markup.raw.yaml.markdown constant",
          "meta.embedded.block.frontmatter constant"
        ],
        "settings": { "foreground": "#d4c78f" }
      },
      {
        "name": "YAML frontmatter punctuation",
        "scope": [
          "markup.raw.yaml.markdown punctuation.separator",
          "meta.embedded.block.frontmatter punctuation.separator",
          "markup.raw.yaml.markdown punctuation.definition.block.sequence.item",
          "meta.embedded.block.frontmatter punctuation.definition.block.sequence.item"
        ],
        "settings": { "foreground": "#8a8494" }
      }
    ]
  }
}
```
