<template>
  <div class="ad-banner-container">
    <div class="ad-banner-container-title">相关推荐</div>

    <!-- 广告 -->
    <div class="ad-banner" v-for="(ad, index) in adbannerList" :key="ad.id" :style="{ background: backgroundColorList[index % backgroundColorList.length] }">
      <div class="ad-content">
        <div class="ad-title">
          <a :href="'/io/' + ad.url" rel="noreferrer" target="_blank">{{ ad.title }}</a>
        </div>
        <div class="ad-subtitle">{{ ad.description }}</div>
      </div>
      <div style="position: absolute; top: 20px; right: 20px; font-size: 24px">{{ emojiList[index % emojiList.length] }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { getAllAdBannerItem } from "../utils/apis";

/**
 * 单个配置项
 * title: 标题
 * folder: 文件夹名称
 * url: 访问链接
 * thumbnail: 缩略图链接
 * previewgif: 预览GIF链接
 * sourcelink: 源代码链接
 * description: 描述
 */
const adbannerList = ref([]);

//  定义背景颜色列表
const backgroundColorList = [
  "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
  "linear-gradient(135deg, #4facfe, #00f2fe)",
  "linear-gradient(135deg, #ff7e5f, #feb47b)",
  "linear-gradient(135deg, #43cea2, #185a9d)",
  "linear-gradient(135deg, #f7971e, #ffd200)",
  "linear-gradient(135deg, #00c6ff, #0072ff)",
  "linear-gradient(135deg, #ff6a00, #ee0979)",
  "linear-gradient(135deg, #00c6ff, #0072ff)",
];

// 定义表情符号列表
const emojiList = ["💬", "⭐", "🎨", "🚀", "🌟", "💡", "📚", "🛠️"];

/**
 * 获取所有广告横幅配置项
 * @returns {Promise<Array>} 返回广告横幅配置项数组
 */
onMounted(async () => {
  const res = await getAllAdBannerItem();
  adbannerList.value = res || [];
});
</script>

<style scoped>
@import url("../assets/components/ad-banner.css");
</style>
