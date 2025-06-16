<template>
  <div class="comment-submit-container">
    <textarea placeholder="输入评论内容..."></textarea>
    <button>提交</button>
  </div>
</template>

<script setup>
import { ref } from "vue";
</script>

<style scoped>
.comment-submit-container {
  margin: 16px auto;
  padding: 16px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.comment-submit-container textarea {
  width: 100%;
  min-height: 120px;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  resize: vertical;
  font-size: 14px;
  line-height: 1.5;
  transition: border-color 0.2s;
}

.comment-submit-container textarea:focus {
  outline: none;
  border-color: #48a9fe;
  box-shadow: 0 0 0 3px rgba(72, 169, 254, 0.2);
}

.comment-submit-container button {
  align-self: flex-end;
  padding: 10px 24px;
  font-size: 15px;
  font-weight: 500;
  color: #fff;
  background: linear-gradient(135deg, #48a9fe 0%, #6d5dfc 100%);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition:
    background 0.3s,
    transform 0.1s;
}
.comment-submit-container button:hover {
  background: linear-gradient(135deg, #6d5dfc 0%, #48a9fe 100%);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
}
.comment-submit-container button:active {
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
}
</style>
