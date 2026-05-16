import { makeAutoObservable } from "mobx";

export class AuthStore {
  accessToken: string | null = null;
  refreshToken: string | null = null;
  id: string | null = null;
  roles: string[] = [];

  constructor() {
    makeAutoObservable(this);
    this.accessToken = localStorage.getItem("accessToken");
    this.refreshToken = localStorage.getItem("refreshToken");
    this.id = localStorage.getItem("id");
    const savedRoles = localStorage.getItem("roles");
    if (savedRoles) {
      try {
        this.roles = JSON.parse(savedRoles);
      } catch {
        this.roles = [];
      }
    }
  }

  setAuth(
    accessToken: string,
    refreshToken: string,
    id: string,
    roles: string[] = [],
  ) {
    this.accessToken = accessToken;
    this.refreshToken = refreshToken;
    this.id = id;
    this.roles = roles;
    localStorage.setItem("accessToken", accessToken);
    localStorage.setItem("refreshToken", refreshToken);
    localStorage.setItem("id", id);
    localStorage.setItem("roles", JSON.stringify(roles));
  }

  setTokens(accessToken: string, refreshToken: string) {
    this.accessToken = accessToken;
    this.refreshToken = refreshToken;
    localStorage.setItem("accessToken", accessToken);
    localStorage.setItem("refreshToken", refreshToken);
  }

  clearTokens() {
    this.accessToken = null;
    this.refreshToken = null;
    this.id = null;
    this.roles = [];
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    localStorage.removeItem("id");
    localStorage.removeItem("roles");
  }

  get isAuthenticated() {
    return !!this.accessToken;
  }

  get isAdmin() {
    return this.roles.includes("admin");
  }

  get isSeller() {
    return this.roles.includes("seller");
  }
}

export const authStore = new AuthStore();
