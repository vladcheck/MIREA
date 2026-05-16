import type { UserResponse } from "@root-shared/types/User";
import { useEffect, useState } from "react";
import useApi from "./useApi";

export default function useUserInfo() {
  const api = useApi();
  const [userInfo, setUserInfo] = useState<undefined | UserResponse>();

  useEffect(() => {
    api
      .getCurrentUserInfo()
      .then((response: any) => {
        if (!response?.data) throw response;
        setUserInfo(response.data);
      })
      .catch((error: string) => {
        console.error(error);
      });
  }, [api]);

  return userInfo;
}
