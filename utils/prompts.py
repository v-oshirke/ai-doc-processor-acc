adverse_events_prompt = """Using Azure OpenAI, analyze the given text to identify adverse events. If an adverse event is found, flag it and provide a summary of the reasons supporting the belief that there is an adverse event in the provided text.
An adverse event refers to any medical occurrence that may occur during or after treatment with a pharmaceutical product, and may or may not be causally related to the treatment. Adverse events do not include inquiries about side effects, the product itself, non human-related reports, missing reporting components, hearsay, dosage/use inquiries, or concerns about the product or disease.
AEs can be categorized as life-threatening or serious. Life-threatening AEs are events that, in the view of the initial reporter, immediately place the patient at risk of death. Serious AEs include events that result in death, life-threatening conditions, inpatient hospitalization, persistent/significant disability, congenital anomalies/birth defects, or other serious conditions.
Adverse events may present as signs, physiological observations, symptoms, changes in laboratory values, diseases, or unexpected therapeutic/clinical benefits.
Serious adverse events include death, life-threatening reactions, hospital admission, events resulting in congenital anomalies/birth defects, events resulting in persistent/significant disability/incapacity, and other medically significant events (e.g., suicide attempts).
Please note that adverse events are not always obvious and may not be communicated as complaints or negative effects. It is important to listen for cues and never solicit AE information, although probing for clarification is allowed.
Examples of adverse events include allergic reactions after product use, death or life-threatening events, hospitalizations, persistent/significant incapacities, congenital anomalies/birth defects, and other important medical events with a reasonable possibility of being caused by the drug.
Adverse events may present as signs (e.g., rash), symptoms (e.g., headache), diseases, changes in laboratory values, physiological observations (e.g., weight change), or as a result of product complaints (e.g., feeling nauseous after taking a medication that smelled like gas or rotten cheese).
When	you	output	the	results	of	your	analysis,	here	is	the	format	of	the	table	I	want	you	to	create.		The	table	should	have	seven	columns,	as	follows:
Call	ID	- This	is	the	reference	to	the	call	transcript	number.		If	there	is	no	call	reference	number,	your	response	should	be	"UNKNOWN"
Reportable	Event	(Y/N)	- If	your	analysis	finds	a	Averse	Event,	this	value	should	be	"Y",	otherwise	"N"
Reporter	- This	value	represents	the	person	that	is	calling	in	the	adverse	event.		This	person	could	be	the	same	as	the	impacted	person	(patient).		If	you	do	not	know	the	name	of	the	reporter,	use	the	value	"UNKNOWN	REPORTER".
Impacted	Individual	- This	value	representers	the	patient	and/or	the	person	who	is	having	the	adverse	event.		If	you	do	not	know	the	name	of	the	impacted	person,	use	the	value	"UNKNOWN	PERSON".
Text	Portion	- This	is	a	short	summary	of	the	adverse	event.
Term	Identified	- This	is	a	one	word	or	two	word	key	phrase	that	was	reported.
Confidence	Score	- This	should	be	a	measure	of	how	confident	you	as	the	LLM	are	regarding	the	reportable	event	after	your	analysis.		Score	should	be	low,	medium,	or	high.		Measurement	of	high	is	based	upon	you	finding	exact	words	that	match	to	an	adverse	event.
Note	that	all	of	this	information	within	the	table	should	be	found	within	your	analysis	results.		Don't	make	anything	up	that you	don't	know	or	have	found	within	the	call	text

Your final output should be JSON in the following format and no other format. Follow this structure exactly, replacing the placeholders with the relevant information extracted from the analysis. Ensure the fields stay the same.

Example JSON output:
[
  {
    "Call Id": "XXXXXX",
    "Reportable Event(s) Identified": "Y",
    "Reporter": "Joe Doe",
    "Impacted Individual": "Jane",
    "Text portion": "My wife got sick to her stomach.",
    "Term identified": "Sick",
    "Confidence Score": "High"
  },
  {
    "Call Id": "XXXXXX",
    "Reportable Event(s) Identified": "Y",
    "Reporter": "Dr. Smith",
    "Impacted Individual": "Patient",
    "Text portion": "Missing pill in the packet",
    "Term identified": "Missing pill",
    "Confidence Score": "Low"
  },
  {
    "Call Id": "XXXXXX",
    "Reportable Event(s) Identified": "Y",
    "Reporter": "Self",
    "Impacted Individual": "\"I\"",
    "Text portion": "I took two pills yesterday instead of one.",
    "Term identified": "instead of",
    "Confidence Score": "Medium"
  }
]
Note: Only provide output strictly in the JSON format shown above. Do not include any other text or explanations outside of this JSON structure."""

drug_name_system_prompt="""Analyze the given text to identify the drug name and then select the file that most closely relates to the drugname.

Example:
Text: "I have been taking ALEVE Caplets for my back pain."
File Name: "ALEVE Caplets 110 Count OCT 2024 2586660241.pdf"

Do not generate anything other than what is included in the list of drugs. Generate the filename exactly. If the drug name is not found in the list, output "UNKNOWN" and do not generate a filename. If the drug name is found in the list, but the filename is not found, output "UNKNOWN FILE NAME" and do not generate a filename. If the drug name is found in the list and the filename is found, output the filename exactly as it appears in the list.
"""

drug_name_user_prompt="""Analyze the given text and the list of drugs to identify the drug name and then select the file that most closely relates to the drugname.\n\nText: \n"""

prompt_3 = "Please summarize the following text: {text}"
prompt_4 = "Answer the question based on the given context: {context} \n Question: {question}"
