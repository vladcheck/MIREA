import { type ToastContent, type ToastOptions, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const CONFIG: ToastOptions = {
  pauseOnHover: false,
  position: "top-right",
};

export default function useNotify() {
  const notify = (
    message: ToastContent<unknown>,
    ms: number = 1000,
    type: ToastOptions["type"] = "default",
  ) => {
    toast(message, {
      ...CONFIG,
      autoClose: ms,
      type,
    });
  };

  const notifyError = (
    message: ToastContent<unknown>,
    ms: number = 1000,
    callback?: () => void,
  ) => {
    toast.error(message, {
      ...CONFIG,
      pauseOnHover: callback ? false : CONFIG.pauseOnHover,
      type: "error",
      autoClose: ms,
      onClose: callback,
    });
  };

  const notifyInfo = (
    message: ToastContent<unknown>,
    ms: number = 1000,
    callback?: () => void,
  ) => {
    toast.info(message, {
      ...CONFIG,
      pauseOnHover: callback ? false : CONFIG.pauseOnHover,
      type: "info",
      autoClose: ms,
      onClose: callback,
    });
  };

  const notifyWarning = (
    message: ToastContent<unknown>,
    ms: number = 1000,
    callback?: () => void,
  ) => {
    toast.warn(message, {
      ...CONFIG,
      pauseOnHover: callback ? false : CONFIG.pauseOnHover,
      type: "warning",
      autoClose: ms,
      onClose: callback,
    });
  };

  const notifySuccess = (
    message: ToastContent<unknown>,
    ms: number = 1000,
    callback?: () => void,
  ) => {
    toast.success(message, {
      ...CONFIG,
      pauseOnHover: callback ? false : CONFIG.pauseOnHover,
      type: "success",
      autoClose: ms,
      onClose: callback,
    });
  };

  return { notify, notifyError, notifyInfo, notifySuccess, notifyWarning };
}
