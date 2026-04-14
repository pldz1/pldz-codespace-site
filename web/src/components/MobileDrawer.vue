<template>
  <transition name="mobile-drawer-fade">
    <div v-show="modelValue" class="mobile-drawer-overlay" @click="onClose"></div>
  </transition>

  <transition name="mobile-drawer-slide">
    <aside v-show="modelValue" class="mobile-drawer">
      <header class="mobile-drawer__header">
        <div class="mobile-drawer__brand">
          <span class="mobile-drawer__logo"></span>
          <div>
            <div class="mobile-drawer__title">{{ title }}</div>
            <div v-if="subtitle" class="mobile-drawer__subtitle">{{ subtitle }}</div>
          </div>
        </div>
        <button class="mobile-drawer__close" type="button" @click="onClose">×</button>
      </header>

      <div class="mobile-drawer__body">
        <div v-if="showNavPlaceholder" class="nav-placeholder"></div>
        <div v-if="$slots.default" class="mobile-drawer__extra">
          <slot></slot>
        </div>
      </div>
    </aside>
  </transition>
</template>

<script setup>
import { onBeforeUnmount, onMounted } from "vue";

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
  title: {
    type: String,
    default: "爬楼的猪 Dev",
  },
  subtitle: {
    type: String,
    default: "",
  },
  showNavPlaceholder: {
    type: Boolean,
    default: true,
  },
  closeAtWidth: {
    type: Number,
    default: 768,
  },
});

const emit = defineEmits(["update:modelValue"]);

function onClose() {
  emit("update:modelValue", false);
}

function handleResize() {
  if (window.innerWidth > props.closeAtWidth && props.modelValue) {
    onClose();
  }
}

onMounted(() => {
  window.addEventListener("resize", handleResize, { passive: true });
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", handleResize);
});
</script>

<style scoped>
.mobile-drawer-overlay {
  position: fixed;
  inset: 0;
  z-index: 70;
  background: rgba(15, 23, 42, 0.28);
}

.mobile-drawer {
  position: fixed;
  inset: 0 auto 0 0;
  z-index: 80;
  width: min(312px, calc(100vw - 32px));
  background: #f8fafc;
  border-right: 1px solid #e6edf5;
  box-shadow: 0 18px 38px rgba(15, 23, 42, 0.12);
  overflow-y: auto;
  overflow-x: hidden;
  overscroll-behavior: contain;
  -webkit-overflow-scrolling: touch;
}

.mobile-drawer__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 18px 14px;
  border-bottom: 1px solid #e6edf5;
}

.mobile-drawer__brand {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.mobile-drawer__logo {
  width: 34px;
  height: 34px;
  flex: 0 0 34px;
  border-radius: 10px;
  background: #ffffff url("../assets/svgs/logo-32.svg") no-repeat center / 22px;
  border: 1px solid #dbe3ef;
}

.mobile-drawer__title {
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
}

.mobile-drawer__subtitle {
  margin-top: 2px;
  font-size: 12px;
  color: #94a3b8;
}

.mobile-drawer__close {
  width: 36px;
  height: 36px;
  border: 1px solid #d9e4f0;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.8);
  color: #334155;
  font-size: 22px;
  line-height: 1;
  cursor: pointer;
}

.mobile-drawer__body {
  padding: 14px 18px 24px;
}

.mobile-drawer__extra {
  margin-top: 18px;
  padding-top: 18px;
  border-top: 1px solid #e5e7eb;
}

.mobile-drawer__extra :deep(p) {
  margin: 0;
  color: #64748b;
  line-height: 1.7;
}

.mobile-drawer__extra :deep(p + p) {
  margin-top: 8px;
}

.mobile-drawer-fade-enter-active,
.mobile-drawer-fade-leave-active {
  transition: opacity 0.2s ease;
}

.mobile-drawer-fade-enter-from,
.mobile-drawer-fade-leave-to {
  opacity: 0;
}

.mobile-drawer-slide-enter-active,
.mobile-drawer-slide-leave-active {
  transition: opacity 0.22s ease, transform 0.22s ease;
}

.mobile-drawer-slide-enter-from,
.mobile-drawer-slide-leave-to {
  opacity: 0;
  transform: translateX(-18px);
}
</style>
