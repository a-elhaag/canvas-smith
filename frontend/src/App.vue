<template>
  <div class="page">
    <header class="section header-box" aria-label="Header">
      HEADER SECTION
    </header>

    <nav class="section nav-box" aria-label="Main Navigation">
      <ul class="nav-list">
        <li><a href="#" aria-label="Home link">Home</a></li>
        <li><span class="sep">|</span></li>
        <li><a href="#" aria-label="About link">About</a></li>
        <li><span class="sep">|</span></li>
        <li><a href="#" aria-label="Services link">Services</a></li>
        <li><span class="sep">|</span></li>
        <li><a href="#" aria-label="Contact link">Contact</a></li>
      </ul>
    </nav>

    <main class="section layout" aria-label="Content area">
      <section class="panel content-panel" aria-label="Main Content Area">
        <h2>Main Content Area</h2>
        <p>Lorem ipsum dolor sit amet consectetur adipisicing elit</p>
        <p>consectetur adipiscing elit</p>
        <button class="cta" @click="handleClick" aria-label="Button action">
          Button
        </button>
        <div v-if="showToast" class="toast" role="status" aria-live="polite">
          Button clicked!
        </div>
      </section>

      <aside class="panel sidebar" aria-label="Sidebar">
        <h3>Sidebar</h3>
        <ul class="menu" aria-label="Sidebar Menu">
          <li>Menu Item 1</li>
          <li>Menu Item 2</li>
          <li>Menu Item 3</li>
        </ul>
      </aside>
    </main>

    <footer class="section footer-box" aria-label="Footer">
      Footer - Copyright©2025
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const showToast = ref(false)

function handleClick() {
  showToast.value = !showToast.value
  if (showToast.value) {
    setTimeout(() => {
      showToast.value = false
    }, 1500)
  }
}
</script>

<style scoped>
:root {
  --border: #000;
  --bg: #fff;
  --muted: #555;
}

* {
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
}

.page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 16px;
}

.section {
  border: 4px solid var(--border);
  padding: 16px;
  margin: 14px 0;
  background: var(--bg);
}

.header-box {
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
  font-size: 18px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.nav-box {
  font-family: Arial, sans-serif;
}

.nav-list {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0;
  margin: 0;
  list-style: none;
  font-size: 14px;
}

.nav-list a {
  text-decoration: none;
  color: #000;
  padding: 2px 6px;
}

.sep {
  color: #000;
  opacity: 0.7;
  padding: 0 4px;
}

.layout {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 20px;
  align-items: start;
}

.panel {
  padding: 18px;
}

.content-panel h2 {
  margin: 0 0 8px 0;
  font-size: 18px;
}

.content-panel p {
  margin: 6px 0;
  color: #333;
}

.cta {
  margin-top: 12px;
  padding: 10px 16px;
  border: 2px solid #000;
  background: #fff;
  cursor: pointer;
  font-weight: 600;
}

.toast {
  display: inline-block;
  margin-top: 10px;
  padding: 8px 12px;
  border: 1px solid #000;
  background: #f5f5f5;
  font-size: 14px;
  border-radius: 4px;
}

.sidebar h3 {
  margin-top: 0;
  font-size: 16px;
}

.menu {
  list-style: none;
  padding: 0;
  margin: 0;
}

.menu li {
  padding: 6px 0;
  border-bottom: 1px solid #eee;
  color: #333;
}

.footer-box {
  font-size: 14px;
  display: block;
}

@media (max-width: 900px) {
  .layout {
    grid-template-columns: 1fr;
  }
}
</style>