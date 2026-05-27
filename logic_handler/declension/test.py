from engine import DeclensionEngine

engine = DeclensionEngine()
forms = engine.declense("rai", gender="m")
forms = engine.declense("sakhi", gender="m")
forms = engine.declense("prakopana", gender="f")
forms
# → {("Nom","Sg"): ["rāmaḥ"], ("Acc","Sg"): ["rāmam"], …}
