<template>
  <router-view v-slot="{ Component }">
    <keep-alive>
      <component :is="Component" />
    </keep-alive>
  </router-view>
  <input type="file" id="global-image-upload-input" accept="image/*" style="display: none" />
</template>
