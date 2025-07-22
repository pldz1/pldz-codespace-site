<template>
  <div class="card-placeholder" :style="{ width: width, padding: padding }">
    <div v-for="(line, idx) in lines" :key="idx" :class="['placeholder-line', line]"></div>
  </div>
</template>

<script setup>
// 接收行数和样式配置
const props = defineProps({
  /**
   * placeholder 行长度数组，可选 'long'、'medium'、'short'
   * 默认五行：100%、80%、80%、60%、100%
   */
  lines: {
    type: Array,
    default: () => ["long", "medium", "medium", "short", "long"],
  },
  /** 宽度，如 '300px'、'100%' 等 */
  width: {
    type: String,
    default: "300px",
  },
  /** 内边距，如 '20px' */
  padding: {
    type: String,
    default: "20px",
  },
});
</script>

<style scoped>
/* 卡片容器样式 */
.card-placeholder {
  border-radius: 8px;
  background: #f0f0f0;
  margin: 20px auto;
}

/* 骨架行基础样式 */
.placeholder-line {
  height: 12px;
  border-radius: 6px;
  background: #e0e0e0;
  position: relative;
  overflow: hidden;
  margin-bottom: 12px;
}
.placeholder-line.long {
  width: 100%;
}
.placeholder-line.medium {
  width: 80%;
}
.placeholder-line.short {
  width: 60%;
}
.placeholder-line:last-child {
  margin-bottom: 0;
}

/* 闪光动画 */
@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}
.placeholder-line::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 50%;
  height: 100%;
  background: linear-gradient(to right, rgba(255, 255, 255, 0) 0%, rgba(255, 255, 255, 0.6) 50%, rgba(255, 255, 255, 0) 100%);
  animation: shimmer 1.5s infinite;
}
</style>
