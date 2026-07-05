<style>
#app {
  margin-top: 60px;
  min-height: 100vh;
  isolation: isolate;
  position: relative;
}

.speck-field {
  position: fixed;
  inset: 0;
  z-index: 0;
  overflow: hidden;
  pointer-events: none;
  background: #f7f8fa;
}

.speck-field span {
  position: absolute;
  display: block;
  width: var(--size);
  height: var(--size);
  left: var(--left);
  top: var(--top);
  border-radius: 999px;
  background: rgba(0, 0, 0, var(--alpha));
  animation: speck-drift var(--duration) ease-in-out infinite alternate;
  animation-delay: var(--delay);
}

.speck-field span:nth-child(1) { --size: 3px; --left: 4%; --top: 12%; --alpha: 0.9; --duration: 12s; --delay: -2s; }
.speck-field span:nth-child(2) { --size: 4px; --left: 10%; --top: 68%; --alpha: 0.78; --duration: 15s; --delay: -8s; }
.speck-field span:nth-child(3) { --size: 3px; --left: 16%; --top: 35%; --alpha: 0.88; --duration: 13s; --delay: -4s; }
.speck-field span:nth-child(4) { --size: 5px; --left: 21%; --top: 18%; --alpha: 0.7; --duration: 17s; --delay: -11s; }
.speck-field span:nth-child(5) { --size: 4px; --left: 25%; --top: 84%; --alpha: 0.76; --duration: 14s; --delay: -6s; }
.speck-field span:nth-child(6) { --size: 3px; --left: 31%; --top: 27%; --alpha: 0.92; --duration: 16s; --delay: -3s; }
.speck-field span:nth-child(7) { --size: 4px; --left: 36%; --top: 61%; --alpha: 0.8; --duration: 12s; --delay: -9s; }
.speck-field span:nth-child(8) { --size: 5px; --left: 41%; --top: 10%; --alpha: 0.68; --duration: 18s; --delay: -5s; }
.speck-field span:nth-child(9) { --size: 3px; --left: 46%; --top: 47%; --alpha: 0.95; --duration: 15s; --delay: -12s; }
.speck-field span:nth-child(10) { --size: 4px; --left: 51%; --top: 75%; --alpha: 0.74; --duration: 19s; --delay: -7s; }
.speck-field span:nth-child(11) { --size: 5px; --left: 57%; --top: 91%; --alpha: 0.64; --duration: 14s; --delay: -10s; }
.speck-field span:nth-child(12) { --size: 3px; --left: 62%; --top: 33%; --alpha: 0.9; --duration: 16s; --delay: -1s; }
.speck-field span:nth-child(13) { --size: 4px; --left: 68%; --top: 14%; --alpha: 0.78; --duration: 13s; --delay: -6s; }
.speck-field span:nth-child(14) { --size: 3px; --left: 72%; --top: 53%; --alpha: 0.96; --duration: 18s; --delay: -13s; }
.speck-field span:nth-child(15) { --size: 5px; --left: 77%; --top: 82%; --alpha: 0.66; --duration: 17s; --delay: -4s; }
.speck-field span:nth-child(16) { --size: 4px; --left: 82%; --top: 24%; --alpha: 0.8; --duration: 12s; --delay: -9s; }
.speck-field span:nth-child(17) { --size: 3px; --left: 87%; --top: 64%; --alpha: 0.92; --duration: 15s; --delay: -2s; }
.speck-field span:nth-child(18) { --size: 4px; --left: 93%; --top: 42%; --alpha: 0.74; --duration: 16s; --delay: -8s; }
.speck-field span:nth-child(19) { --size: 3px; --left: 8%; --top: 91%; --alpha: 0.94; --duration: 14s; --delay: -11s; }
.speck-field span:nth-child(20) { --size: 5px; --left: 19%; --top: 8%; --alpha: 0.62; --duration: 20s; --delay: -5s; }
.speck-field span:nth-child(21) { --size: 4px; --left: 33%; --top: 78%; --alpha: 0.78; --duration: 15s; --delay: -3s; }
.speck-field span:nth-child(22) { --size: 3px; --left: 49%; --top: 20%; --alpha: 0.96; --duration: 13s; --delay: -10s; }
.speck-field span:nth-child(23) { --size: 4px; --left: 66%; --top: 70%; --alpha: 0.82; --duration: 18s; --delay: -7s; }
.speck-field span:nth-child(24) { --size: 3px; --left: 79%; --top: 5%; --alpha: 0.9; --duration: 16s; --delay: -12s; }
.speck-field span:nth-child(25) { --size: 5px; --left: 95%; --top: 86%; --alpha: 0.66; --duration: 19s; --delay: -6s; }

@keyframes speck-drift {
  from {
    transform: translate3d(-8px, 6px, 0);
  }
  to {
    transform: translate3d(14px, -18px, 0);
  }
}

.site-nav {
  background: rgba(255, 255, 255, 0.92);
  border-bottom: 1px solid rgba(222, 226, 230, 0.78);
  backdrop-filter: blur(10px);
}

.site-nav .brand-mark {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  color: #111827;
  font-size: 1.35rem;
  font-weight: 800;
  letter-spacing: 0;
  line-height: 1;
  padding: 0.45rem 0.7rem;
  border: 1px solid rgba(17, 24, 39, 0.14);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.78);
  box-shadow: 0 10px 30px rgba(17, 24, 39, 0.08);
}

.site-nav .brand-mark::before {
  content: "";
  width: 0.45rem;
  height: 0.45rem;
  border-radius: 999px;
  background: #22c55e;
  box-shadow:
    0 0 0 0.22rem rgba(34, 197, 94, 0.12),
    0 0 14px rgba(34, 197, 94, 0.45);
}

.site-nav .brand-mark:hover,
.site-nav .brand-mark:focus-visible {
  color: #111827;
  border-color: rgba(17, 24, 39, 0.3);
  background: rgba(255, 255, 255, 0.96);
}

.site-nav,
.app-content,
.modal,
.modal-backdrop {
  position: relative;
}

.site-nav,
.modal,
.modal-backdrop {
  z-index: 30;
}

.app-content {
  z-index: 10;
}

@media (prefers-reduced-motion: reduce) {
  .speck-field span {
    animation: none;
  }
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
    verifySavedToken(savedToken) {
      axios.post('/api/verify-token', {}, { headers: { Authorization: savedToken } })
        .then(() => {
          this.token = savedToken;
          this.isAdmin = true;
        })
        .catch(() => {
          this.handleLogout();
        });
    },
  },
  created() {
    const savedToken = localStorage.getItem('adminToken');
    if (savedToken) {
      this.verifySavedToken(savedToken);
    }
  },
};
</script>

<template>
  <div class="speck-field" aria-hidden="true">
    <span v-for="index in 25" :key="index"></span>
  </div>

  <nav class="site-nav fixed-top">
    <div class="container d-flex align-items-center justify-content-between py-3">
      <RouterLink class="navbar-brand brand-mark text-decoration-none" to="/">phil.log</RouterLink>
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

  <div class="app-content">
    <RouterView v-slot="{ Component }">
      <component :is="Component" :is-admin="isAdmin" :token="token" />
    </RouterView>
  </div>

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


