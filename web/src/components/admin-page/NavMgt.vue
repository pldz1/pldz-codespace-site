<template>
  <div class="content-container">
    <div class="content-header">
      <h1>网站导航管理</h1>
    </div>
    <div class="content-body">
      <div class="error-message" v-if="errorMessage">{{ errorMessage }}</div>

      <div class="content-item">
        <span>网站导航</span>
        <button class="btn btn-primary" @click="onAddNavItem">新增导航项</button>
      </div>
      <div class="content-item" style="border-top: 1px solid #e4e6ea; margin-top: 8px"></div>

      <!-- 网站导航列表 -->
      <div class="row-list">
        <div class="row-item" v-for="(nav, index) in webNavAdMgt.navs" :key="index">
          <!-- 序号 -->
          <div class="row-serial">{{ index + 1 }}</div>

          <div class="row-content">
            <div class="row-block"><span>标题: </span><input type="text" v-model="nav.title" placeholder="请输入导航标题" @change="onSetNavs" /></div>
            <div class="row-block"><span>连接: </span><input type="url" v-model="nav.url" placeholder="https://example.com" @change="onSetNavs" /></div>
            <div class="row-actions">
              <label title="new"> <input type="checkbox" v-model="nav.new" @change="onSetNavs" /> new标签 </label>
              <button @click="onDeleteNavItem(index)">删除</button>
            </div>
          </div>
        </div>
      </div>
      <div class="content-item">
        <span>横幅广告</span>
        <button class="btn btn-primary" @click="onAddAdItem">新增横幅广告</button>
        <div class="content-item" style="border-top: 1px solid #e4e6ea; margin-top: 8px"></div>
      </div>
      <!-- 广告的列表 -->
      <div class="row-list">
        <div class="row-item" v-for="(ad, index) in webNavAdMgt.ads" :key="index">
          <!-- 序号 -->
          <div class="row-serial">{{ index + 1 }}</div>

          <div class="row-content">
            <div class="row-block"><span>标题: </span><input type="text" v-model="ad.title" placeholder="请输入广告标题" @change="onSetAds" /></div>
            <div class="row-block"><span>连接: </span><input type="url" v-model="ad.url" placeholder="https://example.com" @change="onSetAds" /></div>
            <div class="row-block"><span>描述: </span><input type="text" v-model="ad.description" placeholder="请输入广告描述" @change="onSetAds" /></div>
            <div class="row-actions" style="justify-content: right">
              <button @click="onDeleteAdItem(index)">删除</button>
            </div>
          </div>
        </div>
      </div>
      <!-- Codespace内容 -->
      <div class="content-item">
        <span>CodeSpace内容</span>
        <button class="btn btn-primary" @click="onAddCodeSpaceItem">新增CodeSpace项</button>
        <div class="content-item" style="border-top: 1px solid #e4e6ea; margin-top: 8px"></div>
      </div>
      <div class="row-list">
        <div class="row-item" v-for="(cs, index) in webNavAdMgt.codespaces" :key="index">
          <!-- 序号 -->
          <div class="row-serial">{{ index + 1 }}</div>

          <div class="row-content">
            <div class="row-block"><span>标题: </span><input type="text" v-model="cs.title" placeholder="标题" @change="onSetCodeSpaces" /></div>
            <div class="row-block"><span>连接: </span><input type="url" v-model="cs.url" placeholder="https://example.com" @change="onSetCodeSpaces" /></div>
            <div class="row-block"><span>文件夹: </span><input type="text" v-model="cs.folder" placeholder="文件夹" @change="onSetCodeSpaces" /></div>
            <div class="row-block"><span>缩略图: </span><input type="text" v-model="cs.thumbnail" placeholder="缩略图" @change="onSetCodeSpaces" /></div>
            <div class="row-block"><span>预览图: </span><input type="text" v-model="cs.previewgif" placeholder="预览图" @change="onSetCodeSpaces" /></div>
            <div class="row-block"><span>源码连接: </span><input type="text" v-model="cs.sourcelink" placeholder="源码连接" @change="onSetCodeSpaces" /></div>
            <div class="row-block"><span>日期: </span><input type="text" v-model="cs.date" placeholder="日期" @change="onSetCodeSpaces" /></div>
            <div class="row-block"><span>描述: </span><input type="text" v-model="cs.description" placeholder="描述" @change="onSetCodeSpaces" /></div>
            <div class="row-actions" style="justify-content: right">
              <button @click="onDeleteCodeSpaceItem(index)">删除</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { getNavigation, getAllAdBannerItem, getAllACodeSpace, setCodeSpace, setNavigation, setAllAdBannerItems } from "../../utils/apis";
import Toast from "../../utils/toast.js";

const errorMessage = ref("");
const webNavAdMgt = ref({ navs: [], ads: [], codespaces: [] });

/**
 * 获取网站导航数据和广告横幅数据
 */
async function setNavAdCategory() {
  // 获取网站导航数据
  const navs = await getNavigation();
  if (navs) {
    webNavAdMgt.value.navs = navs;
  } else {
    errorMessage.value = "获取网站导航失败，请稍后再试";
    Toast.error("获取网站导航失败，请稍后再试");
  }

  Toast.success("网站导航获取成功");

  const ads = await getAllAdBannerItem();
  if (ads) {
    webNavAdMgt.value.ads = ads;
  } else {
    errorMessage.value = "获取广告横幅失败，请稍后再试";
    Toast.error("获取广告横幅失败，请稍后再试");
  }

  Toast.success("广告横幅获取成功");

  const codespaces = await getAllACodeSpace();
  if (codespaces) {
    webNavAdMgt.value.codespaces = codespaces;
  } else {
    errorMessage.value = "获取Codespace失败，请稍后再试";
    Toast.error("获取Codespace失败，请稍后再试");
  }

  Toast.success("Codespace获取成功");
}

/**
 * 设置网站导航数据
 * 将当前的导航数据保存到服务器
 */
async function onSetNavs() {
  const res = await setNavigation(webNavAdMgt.value.navs);
  if (!res) {
    errorMessage.value = "设置网站导航失败，请稍后再试";
    Toast.error("设置网站导航失败，请稍后再试");
    return;
  }
  Toast.success("网站导航设置成功");
}

/**
 * 设置CodeSpace数据
 * 将当前的CodeSpace数据保存到服务器
 */
async function onSetCodeSpaces() {
  const res = await setCodeSpace(webNavAdMgt.value.codespaces);
  console.error(webNavAdMgt.value.codespaces);
  if (!res) {
    errorMessage.value = "设置Codespace失败，请稍后再试";
    Toast.error("设置Codespace失败，请稍后再试");
    return;
  }
  Toast.success("Codespace设置成功");
}

/**
 * 新增网站导航项
 * 在导航列表中添加一个新的空白项
 */
async function onAddNavItem() {
  webNavAdMgt.value.navs.push({ title: "", url: "", new: false });
  await onSetNavs();
}

/**
 * 新增网站导航项
 * 在导航列表中添加一个新的空白项
 */
async function onAddCodeSpaceItem() {
  webNavAdMgt.value.codespaces.push({ title: "", url: "", new: false });
  await onSetCodeSpaces();
}

/**
 * 删除网站导航项
 * @param index {number} 导航项索引
 */
async function onDeleteNavItem(index) {
  if (!confirm("确定要删除这个导航吗？")) return;
  webNavAdMgt.value.navs.splice(index, 1);
  await onSetNavs();
}

/**
 * 设置网站导航数据
 * 将当前的导航数据保存到服务器
 */
async function onSetAds() {
  const res = await setAllAdBannerItems(webNavAdMgt.value.ads);
  if (!res) {
    errorMessage.value = "设置广告失败，请稍后再试";
    Toast.error("设置广告失败，请稍后再试");
    return;
  }
  Toast.success("广告设置成功");
}

/**
 * 新增网站导航项
 * 在导航列表中添加一个新的空白项
 */
async function onAddAdItem() {
  webNavAdMgt.value.ads.push({
    title: "",
    url: "",
    folder: "",
    thumbnail: "",
    previewgif: "",
    sourcelink: "",
    date: "",
    description: "",
  });
  await onSetAds();
}

/**
 * 删除广告项
 * @param index {number} 广告项索引
 */
async function onDeleteAdItem(index) {
  if (!confirm("确定要删除这个广告吗？")) return;
  webNavAdMgt.value.ads.splice(index, 1);
  await onSetAds();
}

/**
 * 删除codespace项
 * @param index {number} codespace项索引
 */
async function onDeleteCodeSpaceItem(index) {
  if (!confirm("确定要删除这个Codespace吗？")) return;
  webNavAdMgt.value.codespaces.splice(index, 1);
  await onSetCodeSpaces();
}

/**
 * 在组件挂载时获取网站导航和广告数据
 */
onMounted(async () => {
  await setNavAdCategory();
  Toast.success("网站导航和广告数据加载成功");
});
</script>

<style scoped>
@import url("../../assets/components/admin-content.css");

.row-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.row-item {
  display: flex;
  align-items: center;
  padding: 8px;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.row-serial {
  font-size: 18px;
  font-weight: bold;
  color: #555;
  width: 24px;
  text-align: center;
  margin-right: 8px;
  border-right: 2px solid #e0e0e0;
}

.row-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.row-block {
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  align-items: center;
  justify-content: flex-start;
  gap: 8px;
}

.row-block span {
  width: 112px;
  font-weight: 500;
  color: #333;
}

.row-block input[type="text"],
.row-block input[type="url"] {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
}

.row-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.row-actions label {
  display: flex;
  align-items: center;
  font-size: 14px;
  cursor: pointer;
}

.row-actions button {
  padding: 8px 14px;
  font-size: 14px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  background: #e74c3c;
  color: #fff;
  transition: background 0.2s;
}

.row-actions button:hover {
  background: #c0392b;
}
</style>
