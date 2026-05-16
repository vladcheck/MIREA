import { useContext } from "react";
import ApiContext from "../ApiContext";

export default function useApi() {
  const { api } = useContext(ApiContext);
  return api!;
}
