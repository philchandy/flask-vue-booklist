<template>
    <main class="writer-page">
        <section class="writer-shell">
            <div class="writer-toolbar">
                <button type="button" class="ghost-button" @click="$router.push('/')">Back to posts</button>
                <div class="toolbar-actions" v-if="canEdit">
                    <span class="save-state" v-if="statusMessage">{{ statusMessage }}</span>
                    <button type="button" class="ghost-button" @click="handleInlineUploadClick">Upload Image</button>
                    <button type="button" class="primary-button" @click="savePost">Save Post</button>
                </div>
            </div>

            <div class="alert alert-danger" role="alert" v-if="errorMessage">
                {{ errorMessage }}
            </div>

            <div class="writer-layout">
                <aside class="meta-sidebar">
                    <label>
                        <span>Date</span>
                        <input type="date" v-model="postForm.date" :readonly="!canEdit">
                    </label>
                    <label>
                        <span>Read Time</span>
                        <input type="text" v-model="postForm.readTime" placeholder="Optional" :readonly="!canEdit">
                    </label>
                    <label>
                        <span>Book</span>
                        <input type="text" v-model="postForm.book" placeholder="Optional" :readonly="!canEdit">
                    </label>
                    <label>
                        <span>Tags</span>
                        <input type="text" v-model="postForm.tagsInput" placeholder="Writing, Notes" :readonly="!canEdit">
                    </label>
                </aside>

                <article class="writer-card" :class="{ readonly: !canEdit }">
                    <input
                        v-if="canEdit"
                        class="title-editor"
                        type="text"
                        v-model="postForm.title"
                        placeholder="Untitled post"
                        aria-label="Post title">
                    <h1 v-else class="post-title">{{ postForm.title }}</h1>

                    <textarea
                        v-if="canEdit"
                        ref="postText"
                        class="body-editor"
                        v-model="postForm.excerpt"
                        placeholder="Start writing..."
                        @dragenter.prevent="handleDragEnter"
                        @dragover.prevent="handleDragOver"
                        @dragleave="handleDragLeave"
                        @drop.prevent="handleDrop"></textarea>

                    <div class="post-body" v-else>
                        <template v-for="(block, index) in postBodyBlocks(postForm.excerpt)" :key="`post-block-${index}`">
                            <img v-if="block.type === 'image'" class="inline-post-image" :src="block.src" :alt="block.alt">
                            <p v-else-if="block.text">{{ block.text }}</p>
                        </template>
                    </div>

                    <input
                        ref="inlineImageInput"
                        class="visually-hidden"
                        type="file"
                        accept="image/*"
                        @change="handleInlineImageUpload">

                    <aside class="image-panel" v-if="canEdit && inlineImages.length">
                        <div class="image-panel-header">
                            <p>Inline Images</p>
                            <button
                                type="button"
                                class="danger-button"
                                :disabled="selectedInlineImageLineIndex === null"
                                @click="deleteSelectedInlineImage">
                                Delete Selected
                            </button>
                        </div>
                        <div class="inline-image-list">
                            <button
                                v-for="image in inlineImages"
                                :key="`${image.lineIndex}-${image.src}`"
                                type="button"
                                class="inline-image-item"
                                :class="{ selected: selectedInlineImageLineIndex === image.lineIndex }"
                                @click="toggleInlineImageSelection(image.lineIndex)">
                                <img :src="image.src" :alt="image.alt">
                                <span>{{ image.alt }}</span>
                            </button>
                        </div>
                    </aside>
                </article>
            </div>
        </section>
    </main>
</template>

<script>
import axios from 'axios';

export default {
    props: {
        isAdmin: {
            type: Boolean,
            default: false,
        },
        token: {
            type: String,
            default: null,
        },
    },
    data() {
        return {
            isLoading: false,
            isUploadingImage: false,
            selectedInlineImageLineIndex: null,
            errorMessage: '',
            statusMessage: '',
            postForm: this.emptyPostForm(),
        };
    },
    computed: {
        isNewPost() {
            return this.$route.name === 'NewPost';
        },
        canEdit() {
            return this.isAdmin;
        },
        inlineImages() {
            return this.inlineImagesFromText(this.postForm.excerpt);
        },
    },
    watch: {
        '$route.params.postId': {
            handler() {
                this.loadPage();
            },
        },
    },
    methods: {
        emptyPostForm() {
            return {
                id: '',
                title: '',
                date: new Date().toISOString().slice(0, 10),
                readTime: '',
                excerpt: '',
                book: '',
                imageUrl: '',
                tagsInput: '',
            };
        },
        loadPage() {
            this.errorMessage = '';
            this.statusMessage = '';
            this.selectedInlineImageLineIndex = null;

            if (this.isNewPost) {
                this.postForm = this.emptyPostForm();
                return;
            }

            this.isLoading = true;
            axios.get(`/api/posts/${this.$route.params.postId}`)
                .then((res) => {
                    const post = res.data.post;
                    this.postForm = {
                        id: post.id,
                        title: post.title || '',
                        date: post.date || new Date().toISOString().slice(0, 10),
                        readTime: post.readTime || '',
                        excerpt: post.excerpt || '',
                        book: post.book || '',
                        imageUrl: post.imageUrl || '',
                        tagsInput: post.tags?.join(', ') || '',
                    };
                })
                .catch((error) => {
                    console.error(error);
                    this.errorMessage = 'Could not load this post.';
                })
                .finally(() => {
                    this.isLoading = false;
                });
        },
        buildPayload() {
            return {
                title: this.postForm.title || 'Untitled post',
                date: this.postForm.date,
                readTime: this.postForm.readTime,
                excerpt: this.postForm.excerpt,
                book: this.postForm.book,
                imageUrl: this.postForm.imageUrl,
                tags: this.postForm.tagsInput
                    .split(',')
                    .map((tag) => tag.trim())
                    .filter(Boolean),
            };
        },
        savePost() {
            if (!this.canEdit) {
                return;
            }

            this.errorMessage = '';
            this.statusMessage = 'Saving...';
            const headers = { Authorization: this.token };
            const payload = this.buildPayload();
            const request = this.isNewPost
                ? axios.post('/api/posts', payload, { headers })
                : axios.put(`/api/posts/${this.postForm.id}`, payload, { headers });

            request
                .then((res) => {
                    const savedPost = res.data.post || { id: this.postForm.id };
                    this.statusMessage = 'Saved';
                    if (this.isNewPost && savedPost.id) {
                        this.$router.replace(`/posts/${savedPost.id}`);
                    }
                })
                .catch((error) => {
                    console.error(error);
                    this.statusMessage = '';
                    this.errorMessage = error.response?.status === 401
                        ? 'Log in again before saving this post.'
                        : 'Could not save this post.';
                });
        },
        postBodyBlocks(text) {
            return (text || '').split(/\r?\n/).map((line) => {
                const imageMatch = line.trim().match(/^!\[(.*?)]\((.*?)\)$/);
                if (imageMatch) {
                    return {
                        type: 'image',
                        alt: imageMatch[1] || 'Blog post image',
                        src: imageMatch[2],
                    };
                }
                return {
                    type: 'text',
                    text: line.trim(),
                };
            });
        },
        inlineImagesFromText(text) {
            return (text || '').split(/\r?\n/).reduce((images, line, lineIndex) => {
                const imageMatch = line.trim().match(/^!\[(.*?)]\((.*?)\)$/);
                if (imageMatch) {
                    images.push({
                        lineIndex,
                        alt: imageMatch[1] || 'Blog post image',
                        src: imageMatch[2],
                    });
                }
                return images;
            }, []);
        },
        toggleInlineImageSelection(lineIndex) {
            this.selectedInlineImageLineIndex = this.selectedInlineImageLineIndex === lineIndex ? null : lineIndex;
        },
        deleteSelectedInlineImage() {
            if (this.selectedInlineImageLineIndex === null) {
                return;
            }
            const lines = (this.postForm.excerpt || '').split(/\r?\n/);
            lines.splice(this.selectedInlineImageLineIndex, 1);
            this.postForm.excerpt = lines.join('\n');
            this.selectedInlineImageLineIndex = null;
        },
        handleInlineUploadClick() {
            this.$refs.inlineImageInput?.click();
        },
        handleInlineImageUpload(event) {
            const imageFile = event.target.files?.[0];
            if (!imageFile) {
                return;
            }
            this.uploadInlineImages([imageFile]).finally(() => {
                event.target.value = '';
            });
        },
        handleDragEnter(event) {
            if (this.dragHasFiles(event)) {
                event.currentTarget.classList.add('drop-ready');
            }
        },
        handleDragOver(event) {
            if (this.dragHasFiles(event)) {
                event.dataTransfer.dropEffect = this.token ? 'copy' : 'none';
                event.currentTarget.classList.add('drop-ready');
            }
        },
        handleDragLeave(event) {
            if (!event.currentTarget.contains(event.relatedTarget)) {
                event.currentTarget.classList.remove('drop-ready');
            }
        },
        handleDrop(event) {
            event.currentTarget.classList.remove('drop-ready');
            const imageFiles = Array.from(event.dataTransfer?.files || []).filter((file) => file.type.startsWith('image/'));
            if (!imageFiles.length) {
                this.errorMessage = 'Drop an image file into the post text.';
                return;
            }
            this.uploadInlineImages(imageFiles);
        },
        dragHasFiles(event) {
            return Array.from(event.dataTransfer?.types || []).includes('Files');
        },
        uploadInlineImages(imageFiles) {
            if (!this.token) {
                this.errorMessage = 'Log in before uploading images.';
                return Promise.resolve();
            }

            this.isUploadingImage = true;
            this.errorMessage = '';
            this.statusMessage = 'Uploading image...';

            return imageFiles.reduce((uploadQueue, imageFile) => uploadQueue.then(() => {
                const formData = new FormData();
                formData.append('image', imageFile);
                return axios.post('/api/uploads', formData, { headers: { Authorization: this.token } })
                    .then((res) => {
                        const imageName = imageFile.name.replace(/\.[^.]+$/, '') || 'Uploaded image';
                        this.insertImageAtCursor(res.data.url, imageName);
                    });
            }), Promise.resolve())
                .catch((error) => {
                    console.error(error);
                    this.errorMessage = error.response?.status === 401
                        ? 'Log in again before uploading images.'
                        : 'Could not upload that image.';
                })
                .finally(() => {
                    this.isUploadingImage = false;
                    this.statusMessage = '';
                });
        },
        insertImageAtCursor(imageUrl, altText) {
            const textarea = this.$refs.postText;
            const marker = `![${altText.replace(/[\[\]]/g, '')}](${imageUrl})`;
            const currentText = this.postForm.excerpt || '';
            const start = textarea?.selectionStart ?? currentText.length;
            const end = textarea?.selectionEnd ?? currentText.length;
            const before = currentText.slice(0, start);
            const after = currentText.slice(end);
            const prefix = before && !before.endsWith('\n') ? '\n' : '';
            const suffix = after && !after.startsWith('\n') ? '\n' : '';

            this.postForm.excerpt = `${before}${prefix}${marker}${suffix}${after}`;
            this.selectedInlineImageLineIndex = null;
            this.$nextTick(() => {
                const cursorPosition = before.length + prefix.length + marker.length;
                textarea?.focus();
                textarea?.setSelectionRange(cursorPosition, cursorPosition);
            });
        },
    },
    created() {
        this.loadPage();
    },
};
</script>

<style scoped>
.writer-page {
    min-height: calc(100vh - 60px);
    background: transparent;
    color: #1f2937;
    padding: 3.5rem 1.25rem 5rem;
}

.writer-shell {
    width: min(100%, 1180px);
    margin: 0 auto;
}

.writer-layout {
    display: grid;
    grid-template-columns: 220px minmax(0, 1fr);
    align-items: start;
    gap: 1.5rem;
}

.meta-sidebar {
    position: sticky;
    top: 5.5rem;
    display: flex;
    flex-direction: column;
    gap: 1.1rem;
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.78);
    box-shadow: 0 18px 44px rgba(31, 41, 55, 0.06);
    padding: 1rem;
}

.writer-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
}

.toolbar-actions {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-end;
    align-items: center;
    gap: 0.75rem;
}

.writer-card {
    background: #fff;
    border-radius: 14px;
    box-shadow: 0 24px 70px rgba(31, 41, 55, 0.08);
    padding: clamp(2rem, 5vw, 4.5rem);
    transition: box-shadow 180ms ease, transform 180ms ease;
}

.writer-card:hover {
    box-shadow: 0 28px 80px rgba(31, 41, 55, 0.11);
}

.title-editor,
.post-title {
    width: 100%;
    border: 0;
    outline: 0;
    color: #1f2937;
    font-size: clamp(2.4rem, 6vw, 4.5rem);
    font-weight: 700;
    line-height: 1.08;
    letter-spacing: 0;
    margin: 0 0 1.75rem;
}

.title-editor::placeholder {
    color: #a7adb7;
}

.meta-sidebar label {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    color: #6b7280;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.meta-sidebar input {
    width: 100%;
    background: transparent;
    border: 0;
    border-bottom: 1px solid #e5e7eb;
    color: #374151;
    font-size: 0.95rem;
    outline: 0;
    padding: 0.35rem 0;
    transition: border-color 160ms ease;
}

.meta-sidebar input:focus {
    border-color: #9ca3af;
}

.body-editor,
.post-body {
    width: 100%;
    max-width: 72ch;
    min-height: 46vh;
    border: 0;
    outline: 0;
    resize: vertical;
    color: #1f2937;
    font-size: 1.12rem;
    line-height: 1.75;
}

.body-editor::placeholder {
    color: #a7adb7;
}

.body-editor.drop-ready {
    border-radius: 10px;
    box-shadow: inset 0 0 0 2px rgba(107, 114, 128, 0.22);
    background: #fbfbfc;
}

.post-body p {
    margin: 0 0 1rem;
}

.inline-post-image {
    display: block;
    width: 100%;
    aspect-ratio: 16 / 9;
    object-fit: cover;
    border-radius: 10px;
    margin: 1.4rem 0 1.6rem;
    box-shadow: 0 18px 40px rgba(31, 41, 55, 0.1);
}

.image-panel {
    margin-top: 2.25rem;
    border-radius: 12px;
    background: #f9fafb;
    padding: 1rem;
}

.image-panel-header,
.inline-image-list {
    display: flex;
    gap: 0.75rem;
}

.image-panel-header {
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
}

.image-panel-header p {
    margin: 0;
    font-weight: 700;
}

.inline-image-list {
    flex-wrap: wrap;
}

.inline-image-item {
    width: 140px;
    border: 1px solid transparent;
    border-radius: 10px;
    background: #fff;
    padding: 0.4rem;
    text-align: left;
    transition: border-color 160ms ease, box-shadow 160ms ease, transform 160ms ease;
}

.inline-image-item:hover,
.inline-image-item.selected {
    border-color: #9ca3af;
    box-shadow: 0 14px 32px rgba(31, 41, 55, 0.1);
    transform: translateY(-1px);
}

.inline-image-item img {
    width: 100%;
    aspect-ratio: 16 / 9;
    object-fit: cover;
    border-radius: 8px;
}

.inline-image-item span {
    display: block;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    color: #4b5563;
    font-size: 0.8rem;
    margin-top: 0.35rem;
}

.ghost-button,
.primary-button,
.danger-button {
    border: 0;
    border-radius: 999px;
    padding: 0.55rem 0.95rem;
    font-weight: 700;
    transition: background-color 160ms ease, box-shadow 160ms ease, transform 160ms ease;
}

.ghost-button {
    background: transparent;
    color: #4b5563;
}

.ghost-button:hover {
    background: #edf0f4;
}

.primary-button {
    background: #1f2937;
    color: #fff;
    box-shadow: 0 10px 24px rgba(31, 41, 55, 0.18);
}

.primary-button:hover {
    transform: translateY(-1px);
    box-shadow: 0 14px 32px rgba(31, 41, 55, 0.22);
}

.danger-button {
    background: #fee2e2;
    color: #991b1b;
}

.danger-button:disabled {
    opacity: 0.45;
}

.save-state {
    color: #6b7280;
    font-size: 0.9rem;
}

@media (max-width: 800px) {
    .writer-toolbar,
    .toolbar-actions {
        align-items: flex-start;
        flex-direction: column;
    }

    .writer-layout {
        grid-template-columns: 1fr;
    }

    .meta-sidebar {
        position: static;
        display: grid;
        grid-template-columns: 1fr;
    }
}
</style>