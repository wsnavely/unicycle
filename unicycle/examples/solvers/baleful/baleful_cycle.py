import unicycle.unicycle as uc
import pin

icounter = uc.InstructionCounterUnicycle(start=0x00000000, end=0xffffffff)
icounter.mount()
