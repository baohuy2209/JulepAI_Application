from ui.ApplicationWindow import Ui_MainWindow
import re
from julep import Client
import yaml

class ApplicationWindowExt(Ui_MainWindow):
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow
        self.setupSignalAndSlots()
    def setupSignalAndSlots(self):
        self.pushbuttonGenerate.clicked.connect(self.generate)
    def generate(self):
        self.textEditOutput.setText("")
        topic_str = self.lineEditTopic.text()
        api_key = "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDQ1NDg5OTIsImlhdCI6MTczOTM2NDk5Miwic3ViIjoiOGM4YzY3ODgtYmU0ZS01MmI0LWE4ZDQtODBkODM2ODZlZjE4In0.pF36M7qHalQDVo7FCeM09Br-QHDIvs6SLaeOpUi55dCrIxG3icYQopgnMc8rBG3UPwOHaBQj2MJlJX3xBLq_Lg"

        client = Client(api_key=api_key)
        agent = client.agents.create(
            name="Storytelling Agent",
            model="gpt-4o",
            about="You are a creative storytelling agent that can craft engaging stories and generate comic panels based on ideas.",
        )

        task_definition = yaml.safe_load("""
        name: Story and Comic Creator
        description: Create a story based on an idea and generate a 4-panel comic strip illustrating the story.

        main:
          # Step 1: Generate a story and outline into 4 panels
          - prompt:
              - role: system
                content: You are {{agent.name}}. {{agent.about}}
              - role: user
                content: >
                  Based on the idea '{{_.idea}}', write a short story suitable for a 4-panel comic strip.
                  Provide the story and a numbered list of 4 brief descriptions for each panel illustrating key moments in the story.
            unwrap: true

          # Step 2: Extract the panel descriptions and story
          - evaluate:
              story: _.split('1. ')[0].strip()
              panels: re.findall(r'\\d+\\.\\s*(.*?)(?=\\d+\\.\\s*|$)', _)

          # Step 3: Generate images for each panel using the image generator tool
          - foreach:
              in: _.panels
              do:
                tool: image_generator
                arguments:
                  description: _

          # Step 4: Generate a catchy title for the story
          - prompt:
              - role: system
                content: You are {{agent.name}}. {{agent.about}}
              - role: user
                content: >
                  Based on the story below, generate a catchy title.

                  Story: {{outputs[1].story}}
            unwrap: true

          # Step 5: Return the story, the generated images, and the title
          - return:
              title: outputs[3]
              story: outputs[1].story
              comic_panels: "[output.image.url for output in outputs[2]]"
        """)

        task = client.tasks.create(
            agent_id=agent.id,
            **task_definition  # Unpack the task definition
        )
        execution = client.executions.create(
            task_id=task.id,
            input={"topic": topic_str}
        )

        data = client.executions.transitions.stream(execution_id=execution.id)
        end_of_first_data = data.find('}', 730, 770)
        json_string = data[end_of_first_data:]
        json_string = re.sub(r"'([^'\\]*(?:\\.[^'\\]*)*)'", r'"\1"', json_string)

        data_string = f"""{json_string[10:]}"""
        self.textEditOutput.setText(data_string)

    def show(self):
        self.MainWindow.show()