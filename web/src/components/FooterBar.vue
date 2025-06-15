<template>
  <!-- 底部的信息栏 -->
  <footer class="footer">
    <span>{{ privacyData.copyright }}</span>
    <img style="height: 12px; width: 12px; margin-right: 8px; margin-left: 16px" src="https://img.alicdn.com/tfs/TB1..50QpXXXXX7XpXXXXXXXXXX-40-40.png" />
    <a href="https://beian.miit.gov.cn/?spm=5176.28426678.J_9220772140.59.30965181t5PJph#/Integrated/index" rel="noreferrer" target="_blank">{{
      privacyData.ps
    }}</a>
    <a style="margin-left: 16px" href="https://beian.miit.gov.cn/" target="_blank">{{ privacyData.icp }}</a>
  </footer>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { getPrivacyPolicy } from "../utils/apis.js";

const privacyData = ref({ icp: "", copyright: "", ps: "" });

onMounted(async () => {
  const res = await getPrivacyPolicy();
  Object.assign(privacyData.value, res);
});
</script>

<style scoped>
@import url("../assets/components/footer-bar.css");
</style>
