<template>
  <footer class="footer">
    <div class="footer-inner">
      <div class="footer-copy">
        <span>{{ privacyData.copyright }}</span>
        <span class="footer-divider"></span>
        <span>CodeSpace</span>
      </div>

      <div class="footer-links">
        <a href="https://beian.miit.gov.cn/?spm=5176.28426678.J_9220772140.59.30965181t5PJph#/Integrated/index" rel="noreferrer" target="_blank">
          {{ privacyData.ps }}
        </a>
        <a href="https://beian.miit.gov.cn/" target="_blank">{{ privacyData.icp }}</a>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { getPrivacyPolicy } from "../utils/apis";

const privacyData = ref({ icp: "", copyright: "", ps: "" });

onMounted(async () => {
  const res = await getPrivacyPolicy();
  Object.assign(privacyData.value, res);
});
</script>

<style scoped>
.footer {
  padding: 8px 0 28px;
}

.footer-inner {
  width: min(1180px, calc(100% - 32px));
  margin: 0 auto;
  padding: 20px 0 0;
  border-top: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  color: #94a3b8;
  font-size: 13px;
}

.footer-copy,
.footer-links {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.footer-divider {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #cbd5e1;
}

.footer-links a {
  color: #64748b;
  text-decoration: none;
}

.footer-links a:hover {
  color: #2563eb;
}

@media (max-width: 840px) {
  .footer-inner {
    width: min(100%, calc(100% - 24px));
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 640px) {
  .footer-inner {
    width: min(100%, calc(100% - 16px));
  }
}
</style>
