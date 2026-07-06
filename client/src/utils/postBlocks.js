export function postBodyBlocks(text) {
    const blocks = [];
    const lines = (text || '').split(/\r?\n/);
    let isCodeBlock = false;
    let codeLanguage = '';
    let codeLines = [];

    lines.forEach((line) => {
        const fenceMatch = line.trim().match(/^```([A-Za-z0-9_+#.-]*)\s*$/);

        if (fenceMatch) {
            if (isCodeBlock) {
                blocks.push({
                    type: 'code',
                    language: codeLanguage,
                    code: codeLines.join('\n'),
                });
                isCodeBlock = false;
                codeLanguage = '';
                codeLines = [];
                return;
            }

            isCodeBlock = true;
            codeLanguage = fenceMatch[1] || '';
            codeLines = [];
            return;
        }

        if (isCodeBlock) {
            codeLines.push(line);
            return;
        }

        const imageMatch = line.trim().match(/^!\[(.*?)]\((.*?)\)$/);
        if (imageMatch) {
            blocks.push({
                type: 'image',
                alt: imageMatch[1] || 'Blog post image',
                src: imageMatch[2],
            });
            return;
        }

        blocks.push({
            type: 'text',
            text: line.trim(),
        });
    });

    if (isCodeBlock) {
        blocks.push({
            type: 'code',
            language: codeLanguage,
            code: codeLines.join('\n'),
        });
    }

    return blocks;
}
