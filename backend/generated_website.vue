<template>
  <div class="site">
    <!-- Header Section -->
    <header class="header" role="banner" aria-label="Header section">
      <div class="banner">HEADER SECTION</div>
    </header>

    <!-- Navigation Bar -->
    <nav class="navigation" aria-label="Site navigation">
      <ul class="nav-list" role="menubar">
        <li v-for="(link, index) in navLinks" :key="index" role="menuitem">
          <a href="#" class="nav-link">{{ link }}</a>
        </li>
      </ul>
    </nav>

    <!-- Main Content Area with Sidebar -->
    <main class="site-main" role="main" aria-label="Main layout">
      <section class="content-area" aria-label="Main content area">
        <p class="title">Main Content Area</p>
        <p>Lorem ipsum dolor sit amet<br/>consectetur adipiscing elit</p>
        <button class="btn" aria-label="Button">Button</button>
      </section>

      <aside class="sidebar" aria-label="Sidebar">
        <h3 class="sidebar-title">Sidebar</h3>
        <ul class="menu" aria-label="Sidebar menu">
          <li>Menu Item 1</li>
          <li>Menu Item 2</li>
          <li>Menu Item 3</li>
        </ul>
      </aside>
    </main>

    <!-- Footer -->
    <footer class="footer" role="contentinfo" aria-label="Footer">
      Footer - Copyright© 2025
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const navLinks = ref(['Home', 'About', 'Services', 'Contact'])
</script>

<style scoped>
:root {
  --border: #000;
  --bg: #fff;
  --text: #111;
  --gap: 20px;
}

* { box-sizing: border-box; }

.site {
  max-width: 1100px;
  margin: 20px auto;
  padding: 0 16px;
  color: var(--text);
  font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, Arial, "Helvetica Neue", sans-serif;
}

.header, .navigation, .content-area, .sidebar, .footer {
  border: 3px solid var(--border);
  background: var(--bg);
}

.header {
  margin: 20px 0;
}

.banner {
  padding: 16px 20px;
  font-size: 14px;
  letter-spacing: .5px;
  font-weight: 600;
}

.navigation {
  margin: 12px 0 24px;
}

.nav-list {
  display: flex;
  gap: 14px;
  align-items: center;
  padding: 12px 16px;
  margin: 0;
  list-style: none;
}

.nav-link {
  text-decoration: none;
  color: #111;
  font-size: 14px;
}
.nav-list li:not(:last-child)::after {
  content: "";
}
.nav-list li {
  position: relative;
  padding-right: 8px;
}
.nav-list li:not(:last-child)::after {
  content: "|";
  position: absolute;
  right: -10px;
  color: #000;
  font-weight: 600;
}

.site-main {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 24px;
  align-items: start;
  margin: 8px 0 20px;
}

.content-area {
  padding: 18px;
  min-height: 180px;
}

.content-area .title {
  margin: 0 0 8px;
  font-weight: 600;
}

.sidebar {
  padding: 18px;
  min-height: 180px;
}

.sidebar-title {
  margin: 0 0 8px;
}

.menu {
  list-style: none;
  padding: 0;
  margin: 0;
}

.menu li {
  padding: 6px 0;
}

.btn {
  display: inline-block;
  margin-top: 12px;
  padding: 8px 14px;
  border: 2px solid #000;
  background: #fff;
  cursor: pointer;
  font-size: 14px;
}
.btn:hover {
  background: #f5f5f5;
}

.footer {
  margin: 20px 0;
  padding: 12px 16px;
  font-size: 12px;
  text-align: left;
}
@media (max-width: 900px) {
  .site-main {
    grid-template-columns: 1fr;
  }
}
</style>