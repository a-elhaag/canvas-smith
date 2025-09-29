<template>
  <div class="page-layout">
    <header class="panel header" aria-label="Header">
      <div class="panel-box">HEADER</div>
    </header>

    <nav class="panel nav" aria-label="Main navigation">
      <div class="panel-box">Navigation: Home | About | Contact</div>
    </nav>

    <section class="panel content-area" aria-label="Main content area">
      <article class="panel main-content" aria-label="Main Content">
        Main Content
      </article>
      <aside class="panel sidebar" aria-label="Sidebar">
        Sidebar
      </aside>
    </section>

    <footer class="panel footer" aria-label="Footer">
      <div class="panel-box">Footer</div>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'SimpleLayout'
}
</script>

<style scoped>
* {
  box-sizing: border-box;
}
:root {
  --border: #000;
  --bg: #fff;
  --gap: 20px;
}
.page-layout {
  max-width: 1000px;
  margin: 0 auto;
  padding: 16px;
  font-family: Arial, Helvetica, sans-serif;
  color: #111;
}
.panel {
  margin: 12px 0;
}
.panel-box {
  border: 4px solid #000;
  padding: 14px 18px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas;
  font-size: 14px;
  letter-spacing: 0.5px;
  background: #fff;
}
.content-area {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 20px;
}
.main-content {
  min-height: 120px;
}
.sidebar {
  min-height: 120px;
}
@media (max-width: 900px) {
  .content-area {
    grid-template-columns: 1fr;
  }
}
</style>