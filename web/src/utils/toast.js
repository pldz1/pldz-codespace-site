import Toastify from "toastify-js";
import "toastify-js/src/toastify.css";

export default class Toast {
  /**
   * Display an informational toast message.
   * @param {*} messages
   */
  static info(messages) {
    Toastify({
      text: messages,
      duration: 3000,
      newWindow: true,
      close: true,
      gravity: "top",
      position: "right",
      stopOnFocus: true,
      style: {
        background: "#17a2b8",
      },
      onClick: function () {},
    }).showToast();
  }

  /**
   * Display a success toast message.
   * @param {*} messages
   */
  static success(messages) {
    Toastify({
      text: messages,
      duration: 3000,
      newWindow: true,
      close: true,
      gravity: "top",
      position: "right",
      stopOnFocus: true,
      style: {
        background: "#28a745",
      },
      onClick: function () {},
    }).showToast();
  }

  /**
   * Display a warning toast message.
   * @param {*} messages
   */
  static warning(messages) {
    Toastify({
      text: messages,
      duration: 3000,
      newWindow: true,
      close: true,
      gravity: "top",
      position: "right",
      stopOnFocus: true,
      style: {
        background: "#ffb347",
      },
      onClick: function () {},
    }).showToast();
  }

  /**
   * Display an error toast message.
   * @param {*} messages
   */
  static error(messages) {
    Toastify({
      text: messages,
      duration: 3000,
      newWindow: true,
      close: true,
      gravity: "top",
      position: "right",
      stopOnFocus: true,
      style: {
        background: "#ff5f6d",
      },
      onClick: function () {},
    }).showToast();
  }
}
