<style>
#app {
  margin-top: 60px
}

.site-nav {
  background: #fff;
  border-bottom: 1px solid #dee2e6;
}
</style>

<script setup>
  import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <nav class="site-nav fixed-top">
    <div class="container d-flex align-items-center justify-content-between py-3">
      <RouterLink class="navbar-brand fw-bold text-decoration-none text-dark" to="/">Phillip's Blog</RouterLink>
      <div class="nav nav-pills">
        <RouterLink class="nav-link" to="/">Blog</RouterLink>
        <RouterLink class="nav-link" to="/books">Books List</RouterLink>
      </div>
    </div>
  </nav>
  <RouterView />
</template>


