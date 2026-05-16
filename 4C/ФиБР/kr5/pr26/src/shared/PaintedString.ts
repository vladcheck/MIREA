const SGR = (n: number) => `\x1b[${n}m`;

const Color = {
  SGR_RESET: SGR(0),

  SGR_FG_BLACK: SGR(30),
  SGR_FG_RED: SGR(31),
  SGR_FG_GREEN: SGR(32),
  SGR_FG_YELLOW: SGR(33),
  SGR_FG_BLUE: SGR(34),
  SGR_FG_MAGENTA: SGR(35),
  SGR_FG_CYAN: SGR(36),
  SGR_FG_WHITE: SGR(37),

  SGR_FG_BRIGHT_BLACK: SGR(90),
  SGR_FG_BRIGHT_RED: SGR(91),
  SGR_FG_BRIGHT_GREEN: SGR(92),
  SGR_FG_BRIGHT_YELLOW: SGR(93),
  SGR_FG_BRIGHT_BLUE: SGR(94),
  SGR_FG_BRIGHT_MAGENTA: SGR(95),
  SGR_FG_BRIGHT_CYAN: SGR(96),
  SGR_FG_BRIGHT_WHITE: SGR(96),
} as const;

export default class PaintedString {
  private str: string;

  color(pattern: string, color: string) {
    this.str = this.str.replaceAll(pattern, color + pattern + Color.SGR_RESET);
    return this;
  }

  green(pattern: string) {
    return this.color(pattern, Color.SGR_FG_GREEN);
  }

  brightBlue(pattern: string) {
    return this.color(pattern, Color.SGR_FG_BRIGHT_BLUE);
  }

  red(pattern: string) {
    return this.color(pattern, Color.SGR_FG_RED);
  }

  constructor(str: string) {
    this.str = str;
  }

  get out() {
    return this.str;
  }
}
