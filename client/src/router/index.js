import { createRouter, createWebHistory } from 'vue-router'
import Blog from '../components/Blog.vue'
import Books from '../components/Books.vue'
import Ping from '../components/Ping.vue'
import PostEditor from '../components/PostEditor.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Blog',
      component: Blog,
    },
    {
      path: '/books',
      name: 'Books',
      component: Books,
    },
    {
      path: '/posts/new',
      name: 'NewPost',
      component: PostEditor,
    },
    {
      path: '/posts/:postId',
      name: 'PostEditor',
      component: PostEditor,
    },
    {
      path: '/ping',
      name: 'Ping',
      component: Ping
    },
  ]
})

export default router
