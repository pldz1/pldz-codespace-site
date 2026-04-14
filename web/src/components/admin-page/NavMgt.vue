<template>
  <div class="content-container">
    <div class="content-header">
      <h1>网站导航管理</h1>
      <p>配置站点导航、横幅广告与 CodeSpace 展示内容</p>
    </div>

    <div class="content-body">
      <div class="error-banner" v-if="errorMessage">{{ errorMessage }}</div>

      <div v-if="isNavLoading" class="loading-stack">
        <div v-for="n in 6" :key="`nav-skeleton-${n}`" class="loading-card">
          <div class="skeleton-line w-40"></div>
          <div class="skeleton-line w-80" style="margin-top: 12px"></div>
          <div class="skeleton-line w-60" style="margin-top: 12px"></div>
        </div>
      </div>

      <template v-else>
        <section class="section-block">
          <div class="section-head">
            <h2>网站导航</h2>
            <button class="btn btn-outline" @click="onAddNavItem">新增导航项</button>
          </div>

          <div v-if="webNavAdMgt.navs.length" class="list-block">
            <article class="item-card" v-for="(nav, index) in webNavAdMgt.navs" :key="`nav-${index}`">
              <header class="item-card__header">
                <div class="item-card__title">
                  <span class="item-card__badge">导航 #{{ index + 1 }}</span>
                  <span class="item-card__hint" v-if="nav.title">{{ nav.title }}</span>
                </div>
                <div class="item-card__actions">
                  <label class="toggle">
                    <input type="checkbox" v-model="nav.new" @change="onSetNavs" />
                    <span>展示 new</span>
                  </label>
                  <button class="btn btn-danger" @click="onDeleteNavItem(index)">删除</button>
                </div>
              </header>
              <div class="item-card__grid item-card__grid--nav">
                <label class="form-field">
                  <span class="field-label">标题</span>
                  <input class="field-input" type="text" v-model="nav.title" placeholder="请输入导航标题" @change="onSetNavs" />
                </label>
                <label class="form-field">
                  <span class="field-label">链接</span>
                  <input class="field-input" type="url" v-model="nav.url" placeholder="https://example.com" @change="onSetNavs" />
                </label>
              </div>
            </article>
          </div>
          <div v-else class="empty-state">
            <div class="empty-icon">🧭</div>
            <p>当前暂无导航项，点击右上角按钮新增。</p>
          </div>
        </section>

        <section class="section-block">
          <div class="section-head">
            <h2>横幅广告</h2>
            <button class="btn btn-outline" @click="onAddAdItem">新增横幅</button>
          </div>

          <div v-if="webNavAdMgt.ads.length" class="list-block">
            <article class="item-card" v-for="(ad, index) in webNavAdMgt.ads" :key="`ad-${index}`">
              <header class="item-card__header">
                <div class="item-card__title">
                  <span class="item-card__badge">横幅 #{{ index + 1 }}</span>
                  <span class="item-card__hint" v-if="ad.title">{{ ad.title }}</span>
                </div>
                <div class="item-card__actions">
                  <button class="btn btn-danger" @click="onDeleteAdItem(index)">删除</button>
                </div>
              </header>
              <div class="item-card__grid">
                <label class="form-field">
                  <span class="field-label">标题</span>
                  <input class="field-input" type="text" v-model="ad.title" placeholder="请输入广告标题" @change="onSetAds" />
                </label>
                <label class="form-field">
                  <span class="field-label">链接</span>
                  <input class="field-input" type="url" v-model="ad.url" placeholder="https://example.com" @change="onSetAds" />
                </label>
                <label class="form-field">
                  <span class="field-label">文件夹</span>
                  <input class="field-input" type="text" v-model="ad.folder" placeholder="所属文件夹" @change="onSetAds" />
                </label>
                <label class="form-field">
                  <span class="field-label">缩略图</span>
                  <input class="field-input" type="text" v-model="ad.thumbnail" placeholder="缩略图地址" @change="onSetAds" />
                </label>
                <label class="form-field">
                  <span class="field-label">预览图</span>
                  <input class="field-input" type="text" v-model="ad.previewgif" placeholder="预览图地址" @change="onSetAds" />
                </label>
                <label class="form-field">
                  <span class="field-label">源码链接</span>
                  <input class="field-input" type="text" v-model="ad.sourcelink" placeholder="源码链接" @change="onSetAds" />
                </label>
                <label class="form-field">
                  <span class="field-label">日期</span>
                  <input class="field-input" type="text" v-model="ad.date" placeholder="发布日期" @change="onSetAds" />
                </label>
                <label class="form-field form-field--full">
                  <span class="field-label">描述</span>
                  <textarea class="field-input" v-model="ad.description" placeholder="请输入广告描述" @change="onSetAds"></textarea>
                </label>
              </div>
            </article>
          </div>
          <div v-else class="empty-state">
            <div class="empty-icon">🪧</div>
            <p>还没有横幅广告内容，点击右上角按钮新增。</p>
          </div>
        </section>

        <section class="section-block">
          <div class="section-head">
            <h2>CodeSpace 内容</h2>
            <button class="btn btn-outline" @click="onAddCodeSpaceItem">新增 CodeSpace</button>
          </div>

          <div v-if="webNavAdMgt.codespaces.length" class="list-block">
            <article class="item-card" v-for="(cs, index) in webNavAdMgt.codespaces" :key="`cs-${index}`">
              <header class="item-card__header">
                <div class="item-card__title">
                  <span class="item-card__badge">CodeSpace #{{ index + 1 }}</span>
                  <span class="item-card__hint" v-if="cs.title">{{ cs.title }}</span>
                </div>
                <div class="item-card__actions">
                  <button class="btn btn-danger" @click="onDeleteCodeSpaceItem(index)">删除</button>
                </div>
              </header>
              <div class="item-card__grid">
                <label class="form-field">
                  <span class="field-label">标题</span>
                  <input class="field-input" type="text" v-model="cs.title" placeholder="标题" @change="onSetCodeSpaces" />
                </label>
                <label class="form-field">
                  <span class="field-label">链接</span>
                  <input class="field-input" type="url" v-model="cs.url" placeholder="https://example.com" @change="onSetCodeSpaces" />
                </label>
                <label class="form-field">
                  <span class="field-label">文件夹</span>
                  <input class="field-input" type="text" v-model="cs.folder" placeholder="文件夹" @change="onSetCodeSpaces" />
                </label>
                <label class="form-field">
                  <span class="field-label">缩略图</span>
                  <input class="field-input" type="text" v-model="cs.thumbnail" placeholder="缩略图" @change="onSetCodeSpaces" />
                </label>
                <label class="form-field">
                  <span class="field-label">预览图</span>
                  <input class="field-input" type="text" v-model="cs.previewgif" placeholder="预览图" @change="onSetCodeSpaces" />
                </label>
                <label class="form-field">
                  <span class="field-label">源码链接</span>
                  <input class="field-input" type="text" v-model="cs.sourcelink" placeholder="源码连接" @change="onSetCodeSpaces" />
                </label>
                <label class="form-field">
                  <span class="field-label">日期</span>
                  <input class="field-input" type="text" v-model="cs.date" placeholder="日期" @change="onSetCodeSpaces" />
                </label>
                <label class="form-field form-field--full">
                  <span class="field-label">描述</span>
                  <textarea class="field-input" v-model="cs.description" placeholder="描述" @change="onSetCodeSpaces"></textarea>
                </label>
              </div>
            </article>
          </div>
          <div v-else class="empty-state">
            <div class="empty-icon">📦</div>
            <p>尚未配置 CodeSpace 案例。</p>
          </div>
        </section>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { getNavigation, getAllAdBannerItem, getAllACodeSpace, setCodeSpace, setNavigation, setAllAdBannerItems } from "../../utils/apis";
import Toast from "../../utils/toast.js";
import { useLoading } from "../../utils/use-loading";

const errorMessage = ref("");
const webNavAdMgt = ref({ navs: [], ads: [], codespaces: [] });
const { isLoading: isNavLoading, start: startNavLoading, stop: stopNavLoading } = useLoading("admin.nav.fetch");

async function loadNavData() {
  startNavLoading();
  try {
    const navs = await getNavigation();
    if (navs) {
      webNavAdMgt.value.navs = navs;
    } else {
      throw new Error("获取网站导航失败");
    }

    const ads = await getAllAdBannerItem();
    if (ads) {
      webNavAdMgt.value.ads = ads;
    } else {
      throw new Error("获取广告横幅失败");
    }

    const codespaces = await getAllACodeSpace();
    if (codespaces) {
      webNavAdMgt.value.codespaces = codespaces;
    } else {
      throw new Error("获取 CodeSpace 失败");
    }

    errorMessage.value = "";
    Toast.success("导航与展示数据加载成功");
  } catch (error) {
    console.error(error);
    errorMessage.value = error?.message || "获取网站导航数据失败，请稍后再试";
    Toast.error(errorMessage.value);
  } finally {
    stopNavLoading();
  }
}

async function onSetNavs() {
  const res = await setNavigation(webNavAdMgt.value.navs);
  if (!res) {
    errorMessage.value = "设置网站导航失败，请稍后再试";
    Toast.error("设置网站导航失败，请稍后再试");
    return;
  }
  Toast.success("网站导航设置成功");
}

async function onSetCodeSpaces() {
  const res = await setCodeSpace(webNavAdMgt.value.codespaces);
  if (!res) {
    errorMessage.value = "设置 CodeSpace 失败，请稍后再试";
    Toast.error("设置 CodeSpace 失败，请稍后再试");
    return;
  }
  Toast.success("CodeSpace 设置成功");
}

async function onAddNavItem() {
  webNavAdMgt.value.navs.push({ title: "", url: "", new: false });
  await onSetNavs();
}

async function onAddCodeSpaceItem() {
  webNavAdMgt.value.codespaces.push({
    title: "",
    url: "",
    folder: "",
    thumbnail: "",
    previewgif: "",
    sourcelink: "",
    date: "",
    description: "",
  });
  await onSetCodeSpaces();
}

async function onDeleteNavItem(index) {
  if (!confirm("确定要删除这个导航吗？")) return;
  webNavAdMgt.value.navs.splice(index, 1);
  await onSetNavs();
}

async function onSetAds() {
  const res = await setAllAdBannerItems(webNavAdMgt.value.ads);
  if (!res) {
    errorMessage.value = "设置广告失败，请稍后再试";
    Toast.error("设置广告失败，请稍后再试");
    return;
  }
  Toast.success("广告设置成功");
}

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

async function onDeleteAdItem(index) {
  if (!confirm("确定要删除这个广告吗？")) return;
  webNavAdMgt.value.ads.splice(index, 1);
  await onSetAds();
}

async function onDeleteCodeSpaceItem(index) {
  if (!confirm("确定要删除这个 CodeSpace 吗？")) return;
  webNavAdMgt.value.codespaces.splice(index, 1);
  await onSetCodeSpaces();
}

onMounted(async () => {
  await loadNavData();
});
</script>

<style scoped>
@import url("../../assets/components/admin-content.css");

.list-block {
  gap: 16px;
  border: none;
  border-radius: 0;
  padding: 0;
  overflow: visible;
}

.item-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 18px 0;
  border: none;
  border-bottom: 1px solid #e8eef5;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
}

.item-card__header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.item-card__title {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.item-card__badge {
  font-size: 13px;
  font-weight: 600;
  color: #0f172a;
  background: #eef6ff;
  border-radius: 999px;
  padding: 4px 10px;
  border: 1px solid #dbe7f4;
}

.item-card__hint {
  font-size: 13px;
  color: #64748b;
  max-width: 220px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-card__actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.item-card__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.item-card__grid--nav {
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-field--full {
  grid-column: 1 / -1;
}

.form-field textarea.field-input {
  min-height: 104px;
}

.section-block {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.section-head h2 {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.toggle {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #475569;
}

.toggle input {
  width: 16px;
  height: 16px;
}

.full-width {
  grid-column: 1 / -1;
}

textarea {
  min-height: 72px;
}

@media (max-width: 768px) {
  .item-card {
    padding: 16px;
  }

  .item-card__hint {
    max-width: 100%;
  }

  .section-head {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
