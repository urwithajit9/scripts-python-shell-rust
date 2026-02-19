class A:
    def process(self):
        print("A.process")

# super().process() inside B does NOT mean “call A”.
# It means: call the next class in the MRO after B.
# WRONG mental model:super() calls the parent class.
# RIGHT mental model: super() calls the next class in the MRO, not the parent.
class B(A):
    def process(self):
        print("B.process start")
        super().process()
        print("B.process end")


class C(A):
    def process(self):
        print("C.process start")
        super().process()
        print("C.process end")


class D(B, C):
    def process(self):
        print("D.process start")
        super().process()
        print("D.process end")


d = D()
d.process()

# Check MRO
print(D.mro())
