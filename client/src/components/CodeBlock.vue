<template>
    <figure class="code-snippet" :class="{ copied: copyState === 'Copied' }">
        <figcaption class="code-snippet-header">
            <span class="code-language" v-if="language">{{ language }}</span>
            <span class="code-language" v-else>code</span>
            <button
                type="button"
                class="copy-button"
                :aria-label="`${copyState} code snippet`"
                @click.stop="copyCode">
                {{ copyState }}
            </button>
        </figcaption>
        <pre><code><span
            v-for="(token, index) in highlightedTokens"
            :key="index"
            :class="token.className">{{ token.text }}</span></code></pre>
    </figure>
</template>

<script>
const KEYWORD_PATTERN = /\b(?:async|await|break|case|catch|class|const|continue|default|else|export|for|from|function|if|import|let|new|return|switch|try|var|while)\b/;
const TOKEN_PATTERN = /("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`|\/\/.*|\b\d+(?:\.\d+)?\b|\b(?:async|await|break|case|catch|class|const|continue|default|else|export|for|from|function|if|import|let|new|return|switch|try|var|while)\b)/g;

export default {
    props: {
        code: {
            type: String,
            default: '',
        },
        language: {
            type: String,
            default: '',
        },
    },
    data() {
        return {
            copyState: 'Copy',
            copyResetTimer: null,
        };
    },
    computed: {
        highlightedTokens() {
            const tokens = [];
            const source = this.code || '';
            let lastIndex = 0;
            let match;

            TOKEN_PATTERN.lastIndex = 0;
            while ((match = TOKEN_PATTERN.exec(source)) !== null) {
                if (match.index > lastIndex) {
                    tokens.push({ text: source.slice(lastIndex, match.index), className: '' });
                }

                tokens.push({ text: match[0], className: this.tokenClass(match[0]) });
                lastIndex = TOKEN_PATTERN.lastIndex;
            }

            if (lastIndex < source.length) {
                tokens.push({ text: source.slice(lastIndex), className: '' });
            }

            return tokens.length ? tokens : [{ text: '', className: '' }];
        },
    },
    beforeUnmount() {
        window.clearTimeout(this.copyResetTimer);
    },
    methods: {
        tokenClass(token) {
            if (token.startsWith('//')) {
                return 'token-comment';
            }
            if (token.startsWith('"') || token.startsWith('\'') || token.startsWith('`')) {
                return 'token-string';
            }
            if (/^\d/.test(token)) {
                return 'token-number';
            }
            if (KEYWORD_PATTERN.test(token)) {
                return 'token-keyword';
            }
            return '';
        },
        copyCode() {
            const copyText = () => navigator.clipboard.writeText(this.code || '');
            const fallbackCopy = () => {
                const textarea = document.createElement('textarea');
                textarea.value = this.code || '';
                textarea.setAttribute('readonly', '');
                textarea.style.position = 'fixed';
                textarea.style.opacity = '0';
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
            };

            Promise.resolve(navigator.clipboard ? copyText() : fallbackCopy())
                .then(() => {
                    this.copyState = 'Copied';
                    window.clearTimeout(this.copyResetTimer);
                    this.copyResetTimer = window.setTimeout(() => {
                        this.copyState = 'Copy';
                    }, 1400);
                })
                .catch(() => {
                    this.copyState = 'Copy failed';
                    window.clearTimeout(this.copyResetTimer);
                    this.copyResetTimer = window.setTimeout(() => {
                        this.copyState = 'Copy';
                    }, 1400);
                });
        },
    },
};
</script>

<style scoped>
.code-snippet {
    position: relative;
    overflow: hidden;
    margin: 1.35rem 0 1.6rem;
    border: 1px solid rgba(31, 41, 55, 0.06);
    border-radius: 10px;
    background: #f8f9fb;
    color: #242831;
    box-shadow: 0 10px 28px rgba(31, 41, 55, 0.035);
    animation: code-snippet-enter 180ms ease-out;
}

.code-snippet-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    padding: 0.75rem 0.95rem 0;
}

.code-language {
    color: #717783;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    line-height: 1;
    text-transform: uppercase;
}

.copy-button {
    border: 1px solid rgba(31, 41, 55, 0.08);
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.54);
    color: #5f6672;
    font-size: 0.74rem;
    font-weight: 700;
    line-height: 1;
    opacity: 0;
    padding: 0.45rem 0.68rem;
    transition: opacity 180ms ease, background-color 180ms ease, color 180ms ease, border-color 180ms ease;
}

.code-snippet:hover .copy-button,
.copy-button:focus-visible,
.code-snippet.copied .copy-button {
    opacity: 1;
}

.copy-button:hover,
.copy-button:focus-visible {
    background: #fff;
    border-color: rgba(31, 41, 55, 0.14);
    color: #1f2937;
}

pre {
    margin: 0;
    overflow-x: auto;
    padding: 1rem 1.1rem 1.15rem;
}

code {
    display: block;
    min-width: 100%;
    color: inherit;
    font-family: "Cascadia Code", "SFMono-Regular", Consolas, monospace;
    font-size: 0.9rem;
    line-height: 1.7;
    tab-size: 4;
    white-space: pre;
}

.token-keyword {
    color: #6f5a9a;
}

.token-string {
    color: #5f7f62;
}

.token-number {
    color: #8a6046;
}

.token-comment {
    color: #8b929d;
    font-style: italic;
}

@keyframes code-snippet-enter {
    from {
        opacity: 0;
        transform: translateY(4px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@media (prefers-color-scheme: dark) {
    .code-snippet {
        border-color: rgba(255, 255, 255, 0.055);
        background: #1e1f24;
        color: #e4e6eb;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.16);
    }

    .code-language {
        color: #9da3ad;
    }

    .copy-button {
        border-color: rgba(255, 255, 255, 0.08);
        background: rgba(255, 255, 255, 0.035);
        color: #bdc2cb;
    }

    .copy-button:hover,
    .copy-button:focus-visible {
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(255, 255, 255, 0.16);
        color: #f3f4f6;
    }

    .token-keyword {
        color: #c8b6ee;
    }

    .token-string {
        color: #a9c9a6;
    }

    .token-number {
        color: #d7b08f;
    }

    .token-comment {
        color: #858c98;
    }
}

@media (prefers-reduced-motion: reduce) {
    .code-snippet {
        animation: none;
    }
}
</style>
