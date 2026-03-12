# Retry PDF generation with Unicode support, fixing font loading order

from fpdf import FPDF


class PDF(FPDF):
    def header(self):
        self.set_font("DejaVu", "B", 14)
        self.cell(0, 10, "Korean Grammar Tutorial: 으면 / 면", ln=True, align="C")
        self.ln(10)

    def chapter_title(self, title):
        self.set_font("DejaVu", "B", 12)
        self.cell(0, 10, title, ln=True)
        self.ln(5)

    def chapter_body(self, body):
        self.set_font("DejaVu", "", 11)
        self.multi_cell(0, 8, body)
        self.ln()


pdf = PDF()

# Add fonts before using them
pdf.add_font("DejaVu", "", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", uni=True)
pdf.add_font(
    "DejaVu", "B", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", uni=True
)

pdf.add_page()

# Tutorial content
sections = [
    (
        "What is '-으면 / -면'?",
        "Used to express 'if', 'when', or 'in case'.\n\nExample:\n배고프면 밥을 먹어요. (If you're hungry, eat.)\n비가 오면 우산을 가져가요. (If it rains, take an umbrella.)",
    ),
    (
        "How to Use '-으면 / -면'",
        "Rule:\n- Ends in consonant: add '-으면'\n- Ends in vowel: add '-면'\n- 하다 verbs: become '하면'\n\nExamples:\n먹다 → 먹으면 (if [I] eat)\n가다 → 가면 (if [I] go)\n공부하다 → 공부하면 (if [I] study)",
    ),
    (
        "Example Sentences",
        "- 시간이 있으면 만나요. (If you have time, let’s meet)\n- 추우면 창문을 닫아요. (If it’s cold, close the window)\n- 돈이 많으면 여행을 가고 싶어요. (If I have money, I want to travel)\n- 한국어를 공부하면 재미있어요. (Studying Korean is fun)",
    ),
    (
        "Negative Sentences",
        "Use '안 + verb' or '지 않으면'\n\nExamples:\n- 안 먹으면 (If you don’t eat)\n- 공부하지 않으면 (If you don’t study)",
    ),
    (
        "Practice",
        "Translate:\na) If it rains, I’ll stay home.\nb) If I’m tired, I sleep.\nc) If you don’t eat, you’ll be hungry.\n\nTry building sentences with:\n- 가다 (to go)\n- 배우다 (to learn)\n- 마시다 (to drink)",
    ),
    (
        "Quick Quiz",
        "What is the correct form?\n1. 보다 → _________ (if I see)\n2. 크다 → _________ (if it’s big)\n3. 읽다 → _________ (if I read)\n4. 운동하다 → _________ (if I exercise)\n\nAnswers:\n1. 보면\n2. 크면\n3. 읽으면\n4. 운동하면",
    ),
    (
        "Summary",
        "Form | Use\n-면 | After vowel-ending stems\n-으면 | After consonant-ending stems\n-하면 | For 하다 verbs",
    ),
]

for title, body in sections:
    pdf.chapter_title(title)
    pdf.chapter_body(body)

output_path = "/mnt/data/korean_grammar_umyeon_tutorial.pdf"
pdf.output(output_path)

output_path
