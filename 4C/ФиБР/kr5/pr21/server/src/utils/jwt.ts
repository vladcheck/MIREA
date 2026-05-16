import jwt from "jsonwebtoken";

export type TokenType = "access" | "refresh";
type TokenBody = { [key: string]: any };

interface JwtConfig {
  access: {
    secret: string;
    expiresIn: string | number;
  };
  refresh: {
    secret: string;
    expiresIn: string | number;
  };
}

const JWT_CONFIG: JwtConfig = {
  access: {
    secret: "access_secret",
    expiresIn: "1d",
  },
  refresh: {
    secret: "refresh_secret",
    expiresIn: "28d",
  },
};

const refreshTokens = new Set();

class JwtSingleton {
  grantAccessToken(
    sub: string,
    body: TokenBody,
    expiresIn: any = JWT_CONFIG.access.expiresIn,
  ): string {
    return jwt.sign(
      {
        sub,
        ...body,
      },
      JWT_CONFIG.access.secret,
      {
        expiresIn: expiresIn,
      },
    );
  }

  grantRefreshToken(
    sub: string,
    body: TokenBody,
    expiresIn: any = JWT_CONFIG.access.expiresIn,
  ): string {
    return jwt.sign(
      {
        sub,
        ...body,
      },
      JWT_CONFIG.access.secret,
      {
        expiresIn,
      },
    );
  }

  verify(token: string, type: TokenType) {
    const secret = JWT_CONFIG[type].secret;
    return jwt.verify(token, secret);
  }

  isTokenValid(token: string, type: TokenType) {
    if (type === "refresh") {
      return refreshTokens.has(token);
    } else {
      return true; // TODO: добавить условия
    }
  }

  rotateTokens(
    refreshToken: string,
    sub: string,
    accessTokenBody: TokenBody,
    refreshTokenBody: TokenBody,
  ) {
    refreshTokens.delete(refreshToken);

    const newAccessToken = this.grantAccessToken(sub, accessTokenBody);
    const newRefreshToken = this.grantRefreshToken(sub, refreshTokenBody);

    refreshTokens.add(newRefreshToken);
    return { newAccessToken, newRefreshToken };
  }
}

const jwtSingleton = new JwtSingleton();
export default jwtSingleton;
