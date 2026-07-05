<template>
    <main class="blog-page">
        <section class="container py-4">
            <div class="filter-panel p-3 p-md-4 mb-4">
                <div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-3">
                    <div>
                        <p class="fw-semibold mb-1">Filter by tag</p>
                        <p class="text-secondary mb-0 small">Showing {{ filteredPosts.length }} of {{ posts.length }} posts</p>
                    </div>
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
                </div>
            </div>

            <div class="row g-4" v-if="filteredPosts.length">
                <article class="col-md-6" v-for="post in filteredPosts" :key="post.title">
                    <div class="post-card h-100 p-4">
                        <div class="d-flex align-items-center justify-content-between gap-3 mb-3">
                            <time class="text-secondary small" :datetime="post.date">{{ formatDate(post.date) }}</time>
                            <span class="badge text-bg-light border">{{ post.readTime }}</span>
                        </div>
                        <h2 class="h4 mb-3">{{ post.title }}</h2>
                        <p class="text-secondary mb-4">{{ post.excerpt }}</p>
                        <div class="d-flex flex-wrap gap-2 mb-4">
                            <button
                                v-for="tag in post.tags"
                                :key="tag"
                                type="button"
                                class="tag-button"
                                @click="selectedTag = tag">
                                {{ tag }}
                            </button>
                        </div>
                        <p class="fw-semibold mb-0">{{ post.book }}</p>
                    </div>
                </article>
            </div>

            <div class="empty-state p-5 text-center" v-else>
                <h2 class="h4 mb-2">No posts found</h2>
                <p class="text-secondary mb-3">Try another tag to see more reading notes.</p>
                <button type="button" class="btn btn-primary" @click="selectedTag = 'All'">Show All Posts</button>
            </div>
        </section>
    </main>
</template>

<script>
export default {
    data() {
        return {
            selectedTag: 'All',
            posts: [
                {
                    title: 'Building systems that make progress easier',
                    date: '2026-07-02',
                    readTime: '4 min read',
                    excerpt: 'A reflection on how small actions compound into long-term change and why identity matters more than short bursts of motivation.',
                    book: 'Atomic Habits by James Clear',
                    tags: ['Habits', 'Self Improvement'],
                },
                {
                    title: 'Movement, freedom, and restlessness',
                    date: '2026-06-25',
                    readTime: '5 min read',
                    excerpt: 'A short note on what travel writing can reveal about ambition, uncertainty, and the urge to keep searching for something new.',
                    book: 'On the Road by Jack Kerouac',
                    tags: ['Fiction', 'Travel'],
                },
                {
                    title: 'Why simple stories stay memorable',
                    date: '2026-06-12',
                    readTime: '3 min read',
                    excerpt: 'Some books last because they are playful, direct, and easy to return to. This post looks at clarity as a strength.',
                    book: 'Green Eggs and Ham by Dr. Seuss',
                    tags: ['Classic Reads', 'Writing'],
                },
                {
                    title: 'Starting a series and building a world',
                    date: '2026-05-30',
                    readTime: '6 min read',
                    excerpt: 'A look at first books, worldbuilding, and how a story invites readers into a larger universe without explaining everything at once.',
                    book: "Harry Potter and the Philosopher's Stone by J. K. Rowling",
                    tags: ['Fiction', 'Fantasy'],
                },
                {
                    title: 'What makes a reading habit stick',
                    date: '2026-05-18',
                    readTime: '4 min read',
                    excerpt: 'A practical note on choosing books, setting a pace, and keeping a reading list useful instead of letting it become clutter.',
                    book: 'Reading list reflections',
                    tags: ['Habits', 'Reading Process'],
                },
            ],
        };
    },
    computed: {
        tags() {
            const uniqueTags = new Set(['All']);
            this.posts.forEach((post) => {
                post.tags.forEach((tag) => uniqueTags.add(tag));
            });
            return Array.from(uniqueTags);
        },
        filteredPosts() {
            if (this.selectedTag === 'All') {
                return this.sortedPosts;
            }
            return this.sortedPosts.filter((post) => post.tags.includes(this.selectedTag));
        },
        sortedPosts() {
            return [...this.posts].sort((firstPost, secondPost) => new Date(secondPost.date) - new Date(firstPost.date));
        },
    },
    methods: {
        formatDate(date) {
            return new Intl.DateTimeFormat('en', {
                month: 'long',
                day: 'numeric',
                year: 'numeric',
            }).format(new Date(date));
        },
    },
};
</script>

<style scoped>
.blog-page {
    background: linear-gradient(135deg, #f8f5ef 0%, #e9f2f0 100%);
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

.post-card {
    transition: transform 160ms ease, box-shadow 160ms ease;
}

.post-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 16px 36px rgba(33, 37, 41, 0.12);
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
</style>