<style>
#app {
  margin-top: 60px
}

.site-nav {
  background: #fff;
  border-bottom: 1px solid #dee2e6;
}

.nav-actions {
  column-gap: 0.75rem;
  row-gap: 0.5rem;
}

.modal-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}
</style>

<script>
import axios from 'axios';
import { RouterLink, RouterView } from 'vue-router';

export default {
  components: {
    RouterLink,
    RouterView,
  },
  data() {
    return {
      activeLoginModal: false,
      isAdmin: false,
      token: null,
      loginForm: {
        username: '',
        password: '',
      },
      loginMessage: '',
    };
  },
  methods: {
    toggleLoginModal() {
      this.activeLoginModal = !this.activeLoginModal;
      this.loginMessage = '';
      document.body.classList.toggle('modal-open', this.activeLoginModal);
    },
    handleLoginSubmit() {
      axios.post('/api/login', this.loginForm)
        .then((response) => {
          this.token = response.data.token;
          this.isAdmin = true;
          localStorage.setItem('adminToken', response.data.token);
          this.loginForm.username = '';
          this.loginForm.password = '';
          this.toggleLoginModal();
        })
        .catch((error) => {
          console.error(error);
          this.loginMessage = 'Login failed. Check your username and password.';
        });
    },
    handleLogout() {
      this.token = null;
      this.isAdmin = false;
      localStorage.removeItem('adminToken');
    },
  },
  created() {
    const savedToken = localStorage.getItem('adminToken');
    if (savedToken) {
      this.token = savedToken;
      this.isAdmin = true;
    }
  },
};
</script>

<template>
  <nav class="site-nav fixed-top">
    <div class="container d-flex align-items-center justify-content-between py-3">
      <RouterLink class="navbar-brand fw-bold text-decoration-none text-dark" to="/">Phillip's Blog</RouterLink>
      <div class="d-flex align-items-center flex-wrap nav-actions">
        <div class="nav nav-pills">
          <RouterLink class="nav-link" to="/">Blog</RouterLink>
          <RouterLink class="nav-link" to="/books">Books List</RouterLink>
        </div>
        <button
          v-if="!isAdmin"
          type="button"
          class="btn btn-outline-primary btn-sm"
          @click="toggleLoginModal">
          User Login
        </button>
        <button
          v-else
          type="button"
          class="btn btn-outline-secondary btn-sm"
          @click="handleLogout">
          Logout
        </button>
      </div>
    </div>
  </nav>

  <RouterView v-slot="{ Component }">
    <component :is="Component" :is-admin="isAdmin" :token="token" />
  </RouterView>

  <div
    class="modal fade"
    :class="{ show: activeLoginModal, 'd-block': activeLoginModal }"
    tabindex="-1"
    role="dialog">
    <div class="modal-dialog" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">User Login</h5>
          <button
            type="button"
            class="close"
            data-dismiss="modal"
            aria-label="Close"
            @click="toggleLoginModal">
            <span aria-hidden="true">&times;</span>
          </button>
        </div>
        <div class="modal-body">
          <div class="alert alert-danger" role="alert" v-if="loginMessage">
            {{ loginMessage }}
          </div>
          <form @submit.prevent="handleLoginSubmit">
            <div class="mb-3">
              <label for="adminUsername" class="form-label">Username:</label>
              <input
                type="text"
                class="form-control"
                id="adminUsername"
                v-model="loginForm.username"
                placeholder="Enter username">
            </div>
            <div class="mb-3">
              <label for="adminPassword" class="form-label">Password:</label>
              <input
                type="password"
                class="form-control"
                id="adminPassword"
                v-model="loginForm.password"
                placeholder="Enter password">
            </div>
            <div class="modal-actions">
              <button type="submit" class="btn btn-primary btn-sm">Login</button>
              <button type="button" class="btn btn-danger btn-sm" @click="toggleLoginModal">Cancel</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
  <div v-if="activeLoginModal" class="modal-backdrop fade show"></div>
</template>


