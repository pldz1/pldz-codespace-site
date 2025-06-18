import { createStore } from "vuex";

// 博客信息
const authState = {
  namespaced: true,
  state: {
    // 用户信息
    nickname: "",
    username: "",
    avatar: "",
    isadmin: false,
  },
  actions: {
    // 通过 dispatch 调用这个 action，来提交 mutation
    update({ commit }, data) {
      commit("update", data);
    },
    avatar({ commit }, data) {
      commit("avatar", data);
    },
  },
  mutations: {
    // mutation 来更新 authState
    update(state, data) {
      if (data) {
        state.username = data?.username || "";
        state.isadmin = data?.isadmin || false;
        state.nickname = data?.nickname || "";
        state.avatar = data?.avatar || "";
      }
    },
    avatar(state, data) {
      if (data) {
        state.avatar = data;
      }
    },
  },
};

export default createStore({
  modules: { authState },
});
