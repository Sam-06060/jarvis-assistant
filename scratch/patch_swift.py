import re

file_path = "JarvisApp/Sources/ContentView.swift"
with open(file_path, "r") as f:
    content = f.read()

# 1. Add table to MarkdownBlock enum
content = re.sub(
    r"    case spacer\n}",
    r"    case spacer\n    case table([String])\n}",
    content
)

# 2. Add table support to parse method
old_parse = """    static func parse(_ markdown: String) -> [MarkdownBlock] {
        let normalized = normalize(markdown)
        let lines = normalized.replacingOccurrences(of: "\\r\\n", with: "\\n").components(separatedBy: "\\n")
        var blocks: [MarkdownBlock] = []
        var emittedTextBlockCount = 0
        var paragraphBuffer: [String] = []

        func flushParagraph() {"""

new_parse = """    static func parse(_ markdown: String) -> [MarkdownBlock] {
        let normalized = normalize(markdown)
        let lines = normalized.replacingOccurrences(of: "\\r\\n", with: "\\n").components(separatedBy: "\\n")
        var blocks: [MarkdownBlock] = []
        var emittedTextBlockCount = 0
        var paragraphBuffer: [String] = []
        var tableBuffer: [String] = []

        func flushTable() {
            if !tableBuffer.isEmpty {
                blocks.append(.table(tableBuffer))
                tableBuffer.removeAll(keepingCapacity: true)
            }
        }

        func flushParagraph() {"""
content = content.replace(old_parse, new_parse)

old_loop_start = """        for line in lines {
            let trimmed = line.trimmingCharacters(in: .whitespacesAndNewlines)
            if trimmed.isEmpty {
                flushParagraph()
                if blocks.last != .spacer {"""

new_loop_start = """        for line in lines {
            let trimmed = line.trimmingCharacters(in: .whitespacesAndNewlines)
            if trimmed.isEmpty {
                flushParagraph()
                flushTable()
                if blocks.last != .spacer {"""
content = content.replace(old_loop_start, new_loop_start)

# In the loop
old_loop_heading = """            if let heading = parseHeading(trimmed) {
                flushParagraph()
                blocks.append(.heading(heading.level, heading.text))"""

new_loop_heading = """            if isTableRow(trimmed) {
                flushParagraph()
                tableBuffer.append(trimmed)
                continue
            } else {
                flushTable()
            }

            if let heading = parseHeading(trimmed) {
                flushParagraph()
                blocks.append(.heading(heading.level, heading.text))"""
content = content.replace(old_loop_heading, new_loop_heading)

# After loop
old_flush_after = """        flushParagraph()
        while blocks.last == .spacer {"""
new_flush_after = """        flushParagraph()
        flushTable()
        while blocks.last == .spacer {"""
content = content.replace(old_flush_after, new_flush_after)

# 3. Add isTableRow
old_isDivider = """    private static func isDivider(_ line: String) -> Bool {"""
new_isDivider = """    private static func isTableRow(_ line: String) -> Bool {
        let trimmed = line.trimmingCharacters(in: .whitespaces)
        return trimmed.hasPrefix("|") && trimmed.contains("|") && trimmed.count > 3
    }

    private static func isDivider(_ line: String) -> Bool {"""
content = content.replace(old_isDivider, new_isDivider)

# 4. Render Table in MarkdownText
old_switch = """                        )
                    }
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)"""
new_switch = """                        )
                    }
                case .table(let rows):
                    MarkdownTableView(rows: rows)
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)"""
content = content.replace(old_switch, new_switch)

# 5. Add MarkdownTableView at the end of MarkdownText
old_end = """        Text(rendered)
            .font(font)
            .foregroundColor(color)
            .lineSpacing(5)
            .fixedSize(horizontal: false, vertical: true)
            .frame(maxWidth: .infinity, alignment: .leading)
    }
}"""
new_end = old_end + """

private struct MarkdownTableView: View {
    let rows: [String]

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            VStack(alignment: .leading, spacing: 0) {
                let parsedRows = rows.map { parseRow($0) }
                ForEach(Array(parsedRows.enumerated()), id: \\.offset) { index, columns in
                    let isHeader = index == 0
                    let isDivider = isDividerRow(columns)
                    
                    if isDivider {
                        Rectangle()
                            .fill(Color.white.opacity(0.14))
                            .frame(height: 1)
                    } else {
                        HStack(spacing: 24) {
                            ForEach(Array(columns.enumerated()), id: \\.offset) { colIndex, text in
                                Text(text)
                                    .font(.system(size: 15, weight: isHeader ? .bold : .regular, design: .monospaced))
                                    .foregroundColor(.white.opacity(isHeader ? 0.98 : 0.85))
                                    .frame(minWidth: 80, alignment: .leading)
                            }
                        }
                        .padding(.vertical, 10)
                        .padding(.horizontal, 16)
                        .background(
                            isHeader ? Color.white.opacity(0.08) : (index % 2 == 0 ? Color.clear : Color.white.opacity(0.03))
                        )
                    }
                }
            }
            .overlay(
                RoundedRectangle(cornerRadius: 12, style: .continuous)
                    .stroke(Color.white.opacity(0.1), lineWidth: 1)
            )
            .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
        }
        .padding(.vertical, 8)
    }

    private func parseRow(_ row: String) -> [String] {
        let trimmed = row.trimmingCharacters(in: .whitespaces)
        var cols = trimmed.components(separatedBy: "|").map { $0.trimmingCharacters(in: .whitespaces) }
        if cols.first == "" { cols.removeFirst() }
        if cols.last == "" && !cols.isEmpty { cols.removeLast() }
        return cols
    }

    private func isDividerRow(_ cols: [String]) -> Bool {
        return cols.contains { $0.contains("---") }
    }
}"""
content = content.replace(old_end, new_end)

with open(file_path, "w") as f:
    f.write(content)
print("done")
