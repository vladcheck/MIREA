#!/usr/bin/env python3
"""Эмулятор шины МК-51 + внешняя память (аналог Multisim-схемы рис.25).

Моделирует то, что делает схема:
  P0  — мультиплекс AD0-AD7 (адрес при ALE=1, данные при ALE=0),
  U3 74LS373 — защелкивает младший байт адреса по СПАДУ ALE,
  P2  — старший байт A8-A15,
  /RD (P3.7), /WR (P3.6) — строб чтения/записи XRAM,
  /PSEN — строб чтения внешнего ПЗУ программ,
  D1 на P1.0 — светодиод ошибки (1 = горит).
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class ExtMemSystem:
    xram: bytearray = field(default_factory=lambda: bytearray(65536))
    rom: bytearray = field(default_factory=lambda: bytearray(65536))
    latch: int = 0          # содержимое 74LS373 (A0-A7)
    led_error: bool = False  # D1 на P1.0
    ale_log: list = field(default_factory=list)  # (t_us, level) для осциллограммы
    cycles: int = 0

    # --- шина ---
    def _latch_capture(self, addr: int):
        # спад ALE фиксирует A0-A7 в 373
        self.latch = addr & 0xFF

    def movx_write(self, addr: int, data: int):
        """Эмуляция `movx @dptr,a`: ALE↑(адрес на P0) → ALE↓(фиксация) → /WR↓(данные)."""
        addr &= 0xFFFF
        data &= 0xFF
        self._latch_capture(addr)
        assert self.latch == (addr & 0xFF), "latch mismatch"
        assert ((addr >> 8) & 0xFF) == ((addr >> 8) & 0xFF)  # P2 = A8-A15
        self.xram[addr] = data
        self.cycles += 1

    def movx_read(self, addr: int) -> int:
        """Эмуляция `movx a,@dptr`: ALE↑↓ → /RD↓ → данные с шины."""
        addr &= 0xFFFF
        self._latch_capture(addr)
        self.cycles += 1
        return self.xram[addr]

    def rom_read(self, addr: int) -> int:
        """Чтение внешнего ПЗУ (строб /PSEN//RD)."""
        addr &= 0xFFFF
        self._latch_capture(addr)
        self.cycles += 1
        return self.rom[addr]

    # --- тесты из ТЗ ---
    def ram_test(self, start: int, size: int, pattern: int) -> dict:
        """Задание 1: запись паттерна XX в [ZZZ, ZZZ+1К) и чтение с проверкой. LED при несовпадении."""
        start &= 0xFFFF
        pattern &= 0xFF
        self.led_error = False
        first_bad = None
        for off in range(size):
            a = (start + off) & 0xFFFF
            self.movx_write(a, pattern)
            back = self.movx_read(a)
            if back != pattern:
                self.led_error = True
                if first_bad is None:
                    first_bad = {"addr": hex(a), "wrote": hex(pattern), "read": hex(back)}
                break
        return {"ok": not self.led_error, "led": self.led_error,
                "checked": size if first_bad is None else off + 1, "first_bad": first_bad}

    def rom_checksum(self, start: int, size: int) -> int:
        """Задание 2: контрольная сумма области ПЗУ = сумма байтов mod 256 (8-бит)."""
        s = 0
        for off in range(size):
            s = (s + self.rom_read((start + off) & 0xFFFF)) & 0xFF
        return s

    # --- ALE ---
    def gen_ale(self, machine_cycles: int = 4, f_osc_mhz: float = 12.0):
        """ALE: 2 импульса за машинный цикл. Машинный цикл = 12 периодов fosc = 1 мкс при 12 МГц."""
        t_machine = 12.0 / f_osc_mhz  # мкс
        pts = []
        # детализация: 8 точек на машинный цикл (прямоугольник 2 импульса)
        # паттерн одного цикла (доли цикла): H 0-0.2, L 0.2-0.5, H 0.5-0.7, L 0.7-1.0
        pat = [(0.0, 1), (0.2, 1), (0.2, 0), (0.5, 0), (0.5, 1), (0.7, 1), (0.7, 0), (1.0, 0)]
        for c in range(machine_cycles):
            base = c * t_machine
            for frac, lvl in pat:
                pts.append((round(base + frac * t_machine, 4), lvl))
        self.ale_log = pts
        return pts
