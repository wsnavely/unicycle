import unicycle.unicycle as uc
import pin

icounter = uc.InstructionCounterUnicycle(start=0x8048380, end=0x8048b85)
icounter.mount()
