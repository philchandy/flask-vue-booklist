<template>
    <main class="blog-page">
        <section class="container py-4">
            <div class="filter-panel p-3 p-md-4 mb-4">
                <div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-3">
                    <div>
                        <p class="fw-semibold mb-1">Filter by tag</p>
                        <p class="text-secondary mb-0 small" v-if="!isLoading">Showing {{ filteredPosts.length }} of {{ posts.length }} posts</p>
                        <p class="text-secondary mb-0 small" v-else>Loading posts from server...</p>
                    </div>
                    <div class="d-flex flex-column flex-lg-row align-items-lg-center gap-3">
                        <div class="d-flex flex-wrap gap-2">
                            <button
                                v-for="tag in tags"
                                :key="tag"
                                type="button"
                                class="btn btn-sm"
                                :class="selectedTag === tag ? 'btn-primary' : 'btn-outline-secondary'"
                                @click="selectedTag = tag">
                                {{ tag }}
                            </button>
                        </div>
                        <button
                            v-if="isAdmin"
                            type="button"
                            class="btn btn-success btn-sm"
                            @click="$router.push('/posts/new')">
                            New Post
                        </button>
                    </div>
                </div>
            </div>

            <div class="alert alert-danger" role="alert" v-if="errorMessage">
                {{ errorMessage }}
            </div>

            <div class="post-masonry" v-if="filteredPosts.length">
                <article class="post-tile" v-for="post in filteredPosts" :key="post.id">
                    <div class="post-card p-4" role="button" tabindex="0" @click="openPost(post.id)" @keyup.enter="openPost(post.id)">
                        <img
                            v-if="post.imageUrl"
                            class="post-image mb-4"
                            :src="post.imageUrl"
                            :alt="post.title">
                        <div class="d-flex align-items-center justify-content-between gap-3 mb-3">
                            <time class="text-secondary small" :datetime="post.date">{{ formatDate(post.date) }}</time>
                            <span class="badge text-bg-light border" v-if="post.readTime">{{ post.readTime }}</span>
                        </div>
                        <h2 class="h4 mb-3">{{ post.title }}</h2>
                        <div class="post-body text-secondary mb-4">
                            <template v-for="(block, index) in postBodyBlocks(post.excerpt)" :key="`${post.id}-block-${index}`">
                                <img
                                    v-if="block.type === 'image'"
                                    class="inline-post-image"
                                    :src="block.src"
                                    :alt="block.alt">
                                <CodeBlock
                                    v-else-if="block.type === 'code'"
                                    :code="block.code"
                                    :language="block.language" />
                                <p v-else-if="block.text" class="mb-2">{{ block.text }}</p>
                            </template>
                        </div>
                        <div class="d-flex flex-wrap gap-2 mb-4">
                            <button
                                v-for="tag in post.tags"
                                :key="tag"
                                type="button"
                                class="tag-button"
                                @click.stop="selectedTag = tag">
                                {{ tag }}
                            </button>
                        </div>
                        <p class="fw-semibold mb-0" v-if="post.book">{{ post.book }}</p>
                        <div class="post-actions mt-4" v-if="isAdmin">
                            <button type="button" class="btn btn-warning btn-sm" @click.stop="openPost(post.id)">Edit Post</button>
                            <button type="button" class="btn btn-danger btn-sm" @click.stop="deletePost(post.id)">Delete Post</button>
                        </div>
                    </div>
                </article>
            </div>

            <div class="empty-state p-5 text-center" v-else>
                <h2 class="h4 mb-2">No posts found</h2>
                <p class="text-secondary mb-3">Try another tag to see more reading notes.</p>
                <button type="button" class="btn btn-primary" @click="selectedTag = 'All'">Show All Posts</button>
            </div>
        </section>

        <div
            class="modal fade"
            :class="{ show: activePostModal, 'd-block': activePostModal }"
            tabindex="-1"
            role="dialog">
            <div class="modal-dialog modal-lg" role="document">
                <div class="modal-content">
                    <div class="modal-header align-items-start">
                        <h5 class="modal-title">{{ postForm.id ? 'Edit Post' : 'New Post' }}</h5>
                        <button
                            type="button"
                            class="btn-close ms-auto"
                            data-dismiss="modal"
                            aria-label="Close"
                            @click="togglePostModal()"></button>
                    </div>
                    <div class="modal-body">
                        <form @submit.prevent="handlePostSubmit">
                            <div class="row g-3">
                                <div class="col-md-8">
                                    <label for="postTitle" class="form-label">Title</label>
                                    <input id="postTitle" type="text" class="form-control" v-model="postForm.title" required>
                                </div>
                                <div class="col-md-4">
                                    <label for="postDate" class="form-label">Date</label>
                                    <input id="postDate" type="date" class="form-control" v-model="postForm.date" required>
                                </div>
                                <div class="col-md-6">
                                    <label for="postReadTime" class="form-label">Read Time</label>
                                    <input id="postReadTime" type="text" class="form-control" v-model="postForm.readTime" placeholder="4 min read">
                                </div>
                                <div class="col-md-6">
                                    <label for="postBook" class="form-label">Book</label>
                                    <input id="postBook" type="text" class="form-control" v-model="postForm.book">
                                </div>
                                <div class="col-12">
                                    <label for="postExcerpt" class="form-label">Post Text</label>
                                    <textarea
                                        id="postExcerpt"
                                        ref="postExcerpt"
                                        class="form-control post-textarea"
                                        :class="{ 'drop-ready': isDraggingImage }"
                                        rows="7"
                                        v-model="postForm.excerpt"
                                        required
                                        @dragenter.prevent="handlePostTextDragEnter"
                                        @dragover.prevent="handlePostTextDragOver"
                                        @dragleave="handlePostTextDragLeave"
                                        @drop.prevent="handlePostTextDrop"></textarea>
                                    <div class="inline-image-tools mt-2">
                                        <label class="btn btn-outline-secondary btn-sm mb-0" for="inlineImageUpload">
                                            {{ isUploadingImage ? 'Uploading...' : 'Upload Inline Image' }}
                                        </label>
                                        <input
                                            id="inlineImageUpload"
                                            class="visually-hidden"
                                            type="file"
                                            accept="image/*"
                                            :disabled="isUploadingImage"
                                            @change="handleInlineImageUpload">
                                        <span class="text-secondary small">Upload or drag images into the post text.</span>
                                    </div>
                                    <div class="inline-image-manager mt-3" v-if="postFormInlineImages.length">
                                        <div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-2 mb-2">
                                            <p class="fw-semibold mb-0">Inline Images</p>
                                            <button
                                                type="button"
                                                class="btn btn-outline-danger btn-sm"
                                                :disabled="selectedInlineImageLineIndex === null"
                                                @click="deleteSelectedInlineImage">
                                                Delete Selected Image
                                            </button>
                                        </div>
                                        <div class="inline-image-list">
                                            <button
                                                v-for="image in postFormInlineImages"
                                                :key="`${image.lineIndex}-${image.src}`"
                                                type="button"
                                                class="inline-image-item"
                                                :class="{ selected: selectedInlineImageLineIndex === image.lineIndex }"
                                                @click="toggleInlineImageSelection(image.lineIndex)">
                                                <img :src="image.src" :alt="image.alt">
                                                <span>{{ image.alt }}</span>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-12">
                                    <label for="postTags" class="form-label">Tags</label>
                                    <input id="postTags" type="text" class="form-control" v-model="postForm.tagsInput" placeholder="Fiction, Habits, Reading Process">
                                </div>
                            </div>
                            <div class="modal-actions mt-4">
                                <button type="submit" class="btn btn-primary btn-sm">Save Post</button>
                                <button type="button" class="btn btn-danger btn-sm" @click="togglePostModal()">Cancel</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
        <div v-if="activePostModal" class="modal-backdrop fade show"></div>
    </main>
</template>

<script>
import axios from 'axios';
import CodeBlock from './CodeBlock.vue';
import { postBodyBlocks } from '../utils/postBlocks';

export default {
    components: {
        CodeBlock,
    },
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
            activePostModal: false,
            selectedTag: 'All',
            posts: [],
            isLoading: false,
            isUploadingImage: false,
            isDraggingImage: false,
            selectedInlineImageLineIndex: null,
            errorMessage: '',
            postForm: {
                id: '',
                title: '',
                date: new Date().toISOString().slice(0, 10),
                readTime: '',
                excerpt: '',
                book: '',
                imageUrl: '',
                tagsInput: '',
            },
        };
    },
    computed: {
        tags() {
            const uniqueTags = new Set(['All']);
            this.posts.forEach((post) => {
                post.tags?.forEach((tag) => uniqueTags.add(tag));
            });
            return Array.from(uniqueTags);
        },
        filteredPosts() {
            if (this.selectedTag === 'All') {
                return this.sortedPosts;
            }
            return this.sortedPosts.filter((post) => post.tags?.includes(this.selectedTag));
        },
        sortedPosts() {
            return [...this.posts].sort((firstPost, secondPost) => new Date(secondPost.date) - new Date(firstPost.date));
        },
        postFormInlineImages() {
            return this.inlineImagesFromText(this.postForm.excerpt);
        },
    },
    methods: {
        getPosts() {
            this.isLoading = true;
            this.errorMessage = '';
            axios.get('/api/posts')
                .then((res) => {
                    this.posts = res.data.posts;
                })
                .catch((error) => {
                    console.error(error);
                    this.errorMessage = 'Could not load blog posts from the server.';
                })
                .finally(() => {
                    this.isLoading = false;
                });
        },
            openPost(postId) {
                this.$router.push(`/posts/${postId}`);
            },
        buildPostPayload() {
            return {
                title: this.postForm.title,
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
        resetPostForm() {
            this.postForm = {
                id: '',
                title: '',
                date: new Date().toISOString().slice(0, 10),
                readTime: '',
                excerpt: '',
                book: '',
                imageUrl: '',
                tagsInput: '',
            };
            this.selectedInlineImageLineIndex = null;
        },
        togglePostModal(post = null) {
            if (post) {
                this.postForm = {
                    id: post.id,
                    title: post.title,
                    date: post.date,
                    readTime: post.readTime,
                    excerpt: post.excerpt,
                    book: post.book,
                    imageUrl: post.imageUrl || '',
                    tagsInput: post.tags?.join(', ') || '',
                };
                this.selectedInlineImageLineIndex = null;
            } else if (!this.activePostModal) {
                this.resetPostForm();
            }
            this.activePostModal = !this.activePostModal;
            document.body.classList.toggle('modal-open', this.activePostModal);
        },
        handlePostSubmit() {
            const payload = this.buildPostPayload();
            const headers = { Authorization: this.token };
            const request = this.postForm.id
                ? axios.put(`/api/posts/${this.postForm.id}`, payload, { headers })
                : axios.post('/api/posts', payload, { headers });

            request
                .then(() => {
                    this.togglePostModal();
                    this.getPosts();
                })
                .catch((error) => {
                    console.error(error);
                    this.errorMessage = 'Could not save the blog post.';
                });
        },
        deletePost(postId) {
            axios.delete(`/api/posts/${postId}`, { headers: { Authorization: this.token } })
                .then(() => {
                    this.getPosts();
                })
                .catch((error) => {
                    console.error(error);
                    this.errorMessage = 'Could not delete the blog post.';
                });
        },
        postBodyBlocks(text) {
            return postBodyBlocks(text);
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
        handleInlineImageUpload(event) {
            const imageFile = event.target.files?.[0];
            if (!imageFile) {
                return;
            }

            this.uploadInlineImages([imageFile])
                .catch((error) => {
                    console.error(error);
                    this.errorMessage = this.uploadErrorMessage(error, 'Could not upload that image.');
                })
                .finally(() => {
                    event.target.value = '';
                });
        },
        handlePostTextDragEnter(event) {
            if (this.dragHasFiles(event)) {
                this.isDraggingImage = true;
            }
        },
        handlePostTextDragOver(event) {
            if (!this.dragHasFiles(event)) {
                return;
            }

            event.dataTransfer.dropEffect = this.token ? 'copy' : 'none';
            this.isDraggingImage = true;
        },
        handlePostTextDragLeave(event) {
            if (!event.currentTarget.contains(event.relatedTarget)) {
                this.isDraggingImage = false;
            }
        },
        handlePostTextDrop(event) {
            this.isDraggingImage = false;
            const imageFiles = this.imageFilesFromFileList(event.dataTransfer?.files);

            if (!imageFiles.length) {
                this.errorMessage = 'Drop an image file into the post text.';
                return;
            }

            this.uploadInlineImages(imageFiles)
                .catch((error) => {
                    console.error(error);
                    this.errorMessage = this.uploadErrorMessage(error, 'Could not upload the dropped image.');
                });
        },
        dragHasFiles(event) {
            return Array.from(event.dataTransfer?.types || []).includes('Files');
        },
        imageFilesFromFileList(files) {
            return Array.from(files || []).filter((file) => file.type.startsWith('image/'));
        },
        uploadInlineImages(imageFiles) {
            if (!this.token) {
                this.errorMessage = 'Log in before uploading images.';
                return Promise.resolve();
            }

            this.isUploadingImage = true;
            this.errorMessage = '';

            return imageFiles.reduce((uploadQueue, imageFile) => uploadQueue.then(() => {
                const formData = new FormData();
                formData.append('image', imageFile);

                return axios.post('/api/uploads', formData, { headers: { Authorization: this.token } })
                    .then((res) => {
                        const imageName = imageFile.name.replace(/\.[^.]+$/, '') || 'Uploaded image';
                        this.insertImageAtCursor(res.data.url, imageName);
                    });
            }), Promise.resolve()).finally(() => {
                this.isUploadingImage = false;
            });
        },
        uploadErrorMessage(error, fallbackMessage) {
            if (error.response?.status === 401) {
                return 'Your login expired. Log out, log back in, and try the image upload again.';
            }
            return error.response?.data?.message || fallbackMessage;
        },
        insertImageAtCursor(imageUrl, altText) {
            const textarea = this.$refs.postExcerpt;
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
        formatDate(date) {
            return new Intl.DateTimeFormat('en', {
                month: 'long',
                day: 'numeric',
                year: 'numeric',
            }).format(new Date(date));
        },
    },
    created() {
        this.getPosts();
    },
};
</script>

<style scoped>
.blog-page {
    background: transparent;
    min-height: calc(100vh - 60px);
}

.filter-panel,
.empty-state,
.post-card {
    background: #fff;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    box-shadow: 0 12px 30px rgba(33, 37, 41, 0.08);
}

.post-masonry {
    column-count: 2;
    column-gap: 1.5rem;
}

.post-tile {
    display: inline-block;
    width: 100%;
    margin: 0 0 1.5rem;
    break-inside: avoid;
}

.post-card {
    cursor: pointer;
    transition: transform 160ms ease, box-shadow 160ms ease;
}

.post-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 16px 36px rgba(33, 37, 41, 0.12);
}

.post-image,
.post-image-preview,
.inline-post-image {
    display: block;
    width: 100%;
    aspect-ratio: 16 / 9;
    object-fit: cover;
    border-radius: 8px;
    border: 1px solid #dee2e6;
    background: #f8f9fa;
}

.post-image-preview {
    max-height: 260px;
}

.inline-post-image {
    margin: 0.75rem 0 1rem;
}

.post-body p:last-child {
    margin-bottom: 0;
}

.inline-image-tools {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.75rem;
}

.inline-image-manager {
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 0.9rem;
    background: #f8f9fa;
}

.inline-image-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 0.75rem;
}

.inline-image-item {
    display: flex;
    flex-direction: column;
    gap: 0.45rem;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    background: #fff;
    padding: 0.45rem;
    text-align: left;
}

.inline-image-item.selected {
    border-color: #31554d;
    box-shadow: 0 0 0 0.2rem rgba(49, 85, 77, 0.16);
}

.inline-image-item img {
    width: 100%;
    aspect-ratio: 16 / 9;
    object-fit: cover;
    border-radius: 6px;
    background: #e9ecef;
}

.inline-image-item span {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 0.85rem;
}

.post-textarea {
    border-style: dashed;
    transition: border-color 160ms ease, box-shadow 160ms ease, background-color 160ms ease;
}

.post-textarea.drop-ready {
    background: #f4f8f7;
    border-color: #31554d;
    box-shadow: 0 0 0 0.2rem rgba(49, 85, 77, 0.16);
}

.tag-button {
    border: 1px solid #b6c8c3;
    border-radius: 999px;
    background: #f4f8f7;
    color: #31554d;
    font-size: 0.875rem;
    font-weight: 600;
    padding: 0.25rem 0.7rem;
}

.tag-button:hover {
    background: #e3efec;
}

.post-actions,
.modal-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
}

@media (max-width: 768px) {
    .post-masonry {
        column-count: 1;
    }
}
</style>