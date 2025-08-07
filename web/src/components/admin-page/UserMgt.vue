<template>
  <div class="content-container">
    <div class="content-header">
      <h1>用户管理</h1>
    </div>
    <div class="content-body">
      <div class="error-message" v-if="errorMessage">{{ errorMessage }}</div>
      <!-- 网站导航列表 -->
      <div class="row-list">
        <div class="row-item" v-for="(user, index) in userMgt.users" :key="index">
          <!-- 序号 -->
          <div class="row-serial">{{ index + 1 }}</div>

          <div class="row-content">
            <div class="row-block"><span>id: </span><input type="text" v-model="user.id" :disabled="true" /></div>
            <div class="row-block"><span>用户名: </span><input type="text" v-model="user.username" :disabled="true" /></div>
            <div class="row-block"><span>明文密码: </span><input type="text" v-model="user.raw_password" :disabled="true" /></div>
            <div class="row-block"><span>是否管理员: </span><input type="text" v-model="user.isadmin" :disabled="true" /></div>
            <div class="row-block"><span>昵称: </span><input type="text" v-model="user.nickname" :disabled="true" /></div>
            <div class="row-block"><span>头像: </span><input type="text" v-model="user.avatar" :disabled="true" /></div>
            <div class="row-actions">
              <button @click="onDeleteUserByUsername(user.username)">删除</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { getAllUsers, deleteUserByUsername } from "../../utils/apis";
import Toast from "../../utils/toast.js";

const errorMessage = ref("");
const userMgt = ref({ users: [] });

/**
 * 触发删除用户操作
 * @param username
 */
async function onDeleteUserByUsername(username) {
  // 删除用户
  const res = await deleteUserByUsername(username);
  if (res) {
    // 成功删除后，重新获取所有用户数据
    const users = await getAllUsers();
    userMgt.value.users = users.data;
  } else {
    errorMessage.value = "删除用户失败，请稍后再试";
    Toast.error("删除用户失败，请稍后再试");
  }
}

/**
 * 获取所有用户数据
 */
onMounted(async () => {
  Toast.success("用户数据加载成功");
  const users = await getAllUsers();
  userMgt.value.users = users.data;
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

.row-block img {
  width: 60px;
  max-width: 60px;
  height: 60px;
  max-height: 60px;
}

.row-actions {
  display: flex;
  align-items: center;
  justify-content: right;
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
