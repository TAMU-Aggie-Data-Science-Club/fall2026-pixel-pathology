# Pixel Pathology — Deliverables & Timeline

## Project goal

Build an educational skin-lesion classification model using HAM10000, then display its predictions and Grad-CAM heatmaps in a Streamlit demo.

Our initial task is classification across the dataset's seven lesion categories. Grad-CAM highlights regions that contribute to a model prediction. It does not identify exact disease boundaries or prove that a prediction is correct.

This is a learning project, not a diagnostic tool.

## Subteams and responsibilities

We will have three subteams of approximately five members. Members can express preferences, suggest approaches, and discuss changing roles with the PMs.

| Subteam | Semester responsibilities |
| --- | --- |
| Data & Analysis | Dataset exploration, preprocessing, reproducible splits, data quality checks, and later analysis of model errors and dataset limitations. |
| Modeling & Experiments | Transfer learning, baseline training, controlled experiments, evaluation, and model documentation. |
| Explainability & Application | Grad-CAM implementation, heatmap checks, Streamlit interface, and integration with the trained model. |

Each subteam will divide work into individual or paired tasks, name an owner for each task, and share progress and blockers with the PMs. No team lead or coordinator is required.

### PM responsibilities

Abhi and Kaushik will:
- Assign and clarify deliverables.
- Coordinate dependencies between subteams.
- Help members resolve blockers.
- Review integration pull requests before merging into main.
- Track attendance and individual contributions.
- Maintain the project plan and submit weekly PM reports.

## Meetings and communication

Regular project syncs are Fridays from 6–7 PM Central in the Discord Project Sync voice channel.

**Week 1 exception:** No live meeting was held on Friday, October 9. The planned recording was replaced by a written Discord walkthrough and readiness/assignment updates. Participation was tracked through acknowledgments and documented contributions rather than a hidden attendance word.

GitHub issues track assignments, owners, and decisions. Discord is used for questions, coordination, and reminders. PMs post recaps and record attendance.

## Initial dataset

We will begin with HAM10000 from Harvard Dataverse:

https://doi.org/10.7910/DVN/DBW86T

Required downloads:
- HAM10000_images_part_1.zip
- HAM10000_images_part_2.zip
- HAM10000 metadata in its original CSV format

A PM has downloaded the metadata and both image archives, extracted the images, and confirmed that sample images open.

The metadata contains 10,015 image records across seven classes. Full image-to-metadata matching remains to be checked.

PMs will ensure DATA.md records the source, downloaded version, access instructions, citation, and applicable license/use terms before the Week 1 submission.

Keep datasets local under data/raw/. Do not commit raw images, archives, or raw metadata to GitHub.

## Week 4 — Complete the Pipeline and Improve the Baseline

**Due Sunday, November 1, 2026, at noon Central.**
**Progress sync: Friday, October 30, 6–7 PM Central in Project Sync.**

This week combines unfinished implementation work with one focused model improvement and useful visualizations. All catch-up tasks below count toward Week 4. Do not repeat completed work.

**Goal:** Make the existing data → model → app pipeline work together, compare one improvement against the baseline, and clearly show how the model performs.

### Group 1: Data & Analysis

#### Finish and verify the data handoff
- Run the image audit on both HAM10000 image folders and record the results.
- Resolve or document missing/unreadable images without changing raw files.
- Run the combined split exporter and verification script on the real dataset.
- Record split sizes, per-class counts, image coverage, no duplicate assignments, no lesion overlap, and reproducibility.
- Work with Modeling to ensure its loader reads the combined split file and selects train/val/test rows correctly.
- Bring any remaining data setup documentation into agreement with the actual code.

#### Support the Week 4 improvement
- Summarize the class imbalance using a class-count table or chart.
- Agree with Modeling on one imbalance approach for its improvement experiment.
- Help Modeling identify a few misclassified validation images and summarize any patterns.

**Submit:** reusable scripts in src/data/ and commands, verification results, class counts, and brief observations in docs/week4/.

**Talk to Modeling:** confirm the split file loads correctly and agree on imbalance handling.

**Complete when:** another teammate can generate and verify the splits, and Modeling confirms it can use them.

### Group 2: Modeling & Experiments

#### Finish the working baseline handoff
- Align the loader and training script with Data’s combined split file.
- Keep the frozen backbone’s BatchNorm running statistics fixed during head-only training.
- Document the actual training settings, imbalance handling, checkpoint selection, and checkpoint used for evaluation.
- If these corrections change the training run, train and evaluate a corrected baseline. Preserve the earlier results and clearly label the difference.
- Confirm the evaluated checkpoint loads through the shared prediction functions and returns seven probabilities on a real HAM10000 image.
- Coordinate with PMs on checkpoint sharing and give App clear loading instructions.

#### Run one focused improvement
- Choose one change, such as class-weighted loss, balanced sampling, or a learning-rate adjustment.
- Compare it with the corrected baseline using the same validation split and evaluation procedure.
- Report validation macro F1 and a labeled confusion matrix for both runs.
- Briefly explain which classes improved or worsened, including the classes the original baseline never predicted.
- Include a few validation error examples, with help from Data.

A higher score is not required. A reproducible comparison and an honest explanation count as completion.

**Submit:** training/prediction/evaluation code in src/ and settings, commands, results, plots, and contribution notes in docs/week4/.

**Talk to Data:** confirm split compatibility and imbalance handling.
**Talk to App:** provide one agreed checkpoint, prediction interface, class order, and preprocessing.

**Complete when:** the corrected baseline runs, one comparison experiment is evaluated, and App can obtain and load the agreed checkpoint.

### Group 3: Explainability & App

#### Finish the model-connected app
- Build on the completed Week 2 page and merged pending-state work.
- Connect Modeling’s checkpoint-loading and prediction functions.
- Show the readable predicted class, its model probability, and all seven probabilities in a clear chart or table.
- Keep known dataset labels clearly separate from model predictions.
- Use Modeling’s shared preprocessing and class order.
- Preserve image viewing and a clear pending message when the checkpoint is missing.
- Keep the educational-use notice visible.

#### Visualize model behavior
- Display the agreed model’s validation confusion matrix with a short explanation of its main limitations.
- Have another teammate test uploads, dataset samples, known labels, real predictions, and missing-checkpoint behavior.
- Record the model/checkpoint associated with the displayed evaluation results.

**Submit:** code in app/ and setup instructions, test evidence, remaining limitations, and contribution notes in docs/week4/.

**Talk to Modeling:** confirm checkpoint access and the prediction interface.
**Talk to Data:** resolve sample-image or metadata issues.

**Complete when:** another teammate can launch the app, obtain a real prediction, view the performance visualization, and understand the model’s limitations.

**Stretch goal:** add a Grad-CAM overlay after the required prediction flow works. Clearly explain that it highlights regions influencing a prediction, not exact lesion boundaries or proof the prediction is correct.

### Shared standards

- Dataset: HAM10000.
- Keep the existing 70/15/15 lesion-grouped split with seed 42.
- Combined split file: data/processed/splits.csv.
- Columns: image_id, lesion_id, dx, split.
- Split values: train, val, test.
- Class order: akiec, bcc, bkl, df, mel, nv, vasc.
- Use the shared class mapping from src/model.py.
- Use ResNet50 IMAGENET1K_V2 prediction preprocessing; random augmentation is for training only.
- Leave the test set untouched during this week’s comparison.
- Keep raw images, generated split files, and model checkpoints out of GitHub. Commit reproducible code, instructions, and small evaluation summaries/plots.
- Every artifact is for education and research, not diagnosis.

### GitHub and team coordination

- Post a short task breakdown on your team’s Week 4 issue, naming who is handling each task.
- Use branches per task; members working together may share a branch.
- Open task PRs into the team’s agreed integration branch.
- Have a teammate or PM review before merging.
- Include run instructions, evidence, and each member’s contribution.
- PMs review the combined integration PR into main.
- Check in midweek with completed work, remaining work, and blockers.

### Scope limit

Required: finish the existing pipeline, run one model improvement comparison, and show real predictions plus performance results in the app.

Not required this week: multiple architectures, extensive hyperparameter searches, ROC curves, deployment, or a finished Grad-CAM implementation.

## Week 3 — Train our first baseline and connect the app

**Due Sunday, October 25, 2026, at noon Central.**
**Progress sync: Friday, October 23, 6–7 PM Central in Project Sync.**

### This week's goal

Turn our existing code into a working first version:
- Data provides verified image splits.
- Modeling trains and evaluates one baseline.
- App displays real baseline predictions.

Each group must post its task breakdown on its Week 3 issue before starting. Give everyone an identifiable contribution. Members working together on one task may share a branch.

### Shared standards

- Model: ResNet50 with IMAGENET1K_V2 weights.
- Class order: akiec, bcc, bkl, df, mel, nv, vasc.
- Use CLASS_NAMES and CLASS_TO_IDX from src/model.py.
- Use the agreed V2 prediction preprocessing; keep random augmentation for training only.
- Keep the existing 70/15/15 lesion-grouped split with seed 42.
- Prepare images when loading them; do not save preprocessed copies.

Local data layout:
- data/raw/HAM10000_metadata.csv
- data/raw/HAM10000_images_part_1/
- data/raw/HAM10000_images_part_2/

Proposed split-file convention, pending PM confirmation:
- data/processed/splits.csv
- Columns: image_id, lesion_id, dx, split
- Split values: train, val, test

Commit code and instructions. Keep raw images, generated datasets/manifests, and model checkpoints out of GitHub.

### Group 1: Data & Analysis

**Goal:** Give Modeling a verified, reproducible split file it can use for training.

#### URGENT — Week 2 catch-up

**Target completion: Thursday, October 22, so Modeling has time to train.**

- Run the image audit on both image folders and record the results.
- Address missing or unreadable images before finalizing the splits, without modifying raw files.
- Save the split file locally under data/processed/ using the confirmed format.
- Move reusable audit and split code from Colab into src/data/ so it runs locally against data/raw/. Keep the exploration notebook in notebooks/.
- Coordinate with PMs to merge one of duplicate PRs #31 and #33, credit all four contributors, and close the other.
- Open a PR for Melanie's docs/week2/README.md and make sure it matches the actual results.
- Keep generated audit outputs outside data/raw/.

#### Week 3 work

- Keep the existing split method; a new splitting experiment is not required.
- Verify image coverage, no duplicate assignments, no lesion overlap, and reproducibility.
- Report class counts for training, validation, and test splits.
- Agree on one simple training-imbalance approach with Modeling. No comparison experiment is required.
- Provide the command and data-path instructions needed to generate the split file.

**Talk to Modeling:** confirm it can generate and load the split file.
**Talk to App:** confirm sample-image access and known-label lookup.

**Submit:** reusable code in src/data/, exploration in notebooks/, and brief instructions/results in docs/week3/.

**Complete when:** the audit has recorded results, split generation runs, verification passes, and Modeling confirms the handoff works.

### Group 2: Modeling & Experiments

**Goal:** Train one baseline and make its predictions available to App.

#### URGENT — Week 2 handoff and cleanup

Week 2 implementation requirements are complete. Do not repeat the first-training-step assignment.

- Ensure the combined Week 2 submission includes the loader, preprocessing, seven-output model, and recorded real-image training-step results.
- Remove the stale class-mapping TODO comment in src/img_loader.py.
- Fix the manifest example in docs/week2/training_step.md to include .csv.
- Coordinate with PMs on reviewing and publishing the Week 2 integration branch.

#### Week 3 work

- Update the loader to read the confirmed split file and select training or validation rows.
- Use the shared class mapping from src/model.py.
- Freeze the pretrained backbone and train only the seven-class output layer. Keep the frozen backbone's running statistics fixed.
- Use one imbalance approach agreed with Data.
- Train on training images and use validation results to choose the checkpoint. Leave the test set untouched.
- Report validation macro F1 and a confusion matrix.
- Save the checkpoint locally and document how teammates obtain or reproduce it.
- Provide reusable prediction functions that load the checkpoint, prepare an image, and return seven probabilities in the agreed class order.
- Record the training command, dependencies, settings, and results.

**Talk to Data:** confirm split access and imbalance handling.
**Talk to App:** agree on prediction function inputs/outputs and checkpoint location early in the week.

Multiple models, extensive tuning, and fine-tuning the backbone are not required.

**Submit:** code in src/ and brief instructions/results in docs/week3/.

**Complete when:** one baseline training run finishes, validation results are recorded, and the prediction function works on a real image.

### Group 3: Explainability & App

**Goal:** Finish the page and connect real baseline predictions.

#### URGENT — Week 2 catch-up

- Wire known-label lookup into the page.
- Replace the personal Windows path in app/known_label.py with the shared configurable metadata path.
- Remove the hardcoded test lookup.
- Clearly identify dataset labels as known labels, separate from predictions.
- Add a contributions section to docs/week2/app.md.
- Have another member run the app using the documented instructions.
- Coordinate with PMs to open the completed Week 2 integration PR into main.

#### Week 3 work

- Connect Modeling's prediction functions to the existing page.
- Show the predicted class using its readable name, its model probability, and all seven probabilities.
- Keep known labels and model predictions clearly separate.
- Use Modeling's prediction preprocessing and class order.
- If the checkpoint is missing, show a clear pending message and keep image viewing functional.
- Keep the educational-use notice visible.
- Keep Grad-CAM marked pending; heatmaps are planned for Week 4.
- Verify the combined upload/sample-selection, image display, label lookup, and prediction flow.

**Talk to Modeling:** agree on the prediction interface and checkpoint access.
**Talk to Data:** confirm sample-image paths and label lookup.

Split displays, confidence thresholds, extra styling, and Grad-CAM are not required.

**Submit:** code in app/ and brief run instructions in docs/week3/.

**Complete when:** another member can launch the app and view a real baseline prediction. If the model handoff is delayed, submit the finished interface with a clear pending state and document the blocker.

### GitHub and completion requirements

- Create task branches from the integration branch linked to your Week 3 issue.
- Open task PRs into that integration branch.
- Have a teammate or PM review and approve before merging.
- Identify each member's contribution and include run instructions and evidence.
- PMs review combined integration PRs into main.
- Keep Week 2 issues #21–23 open until their required work is completed and merged into main.
- Report blockers early rather than waiting until Sunday.

### Next steps after Week 3

Plan to compare fine-tuning against this baseline and add Grad-CAM in Week 4. Each group should include a short note in its submission describing its next task and any dependency on another group.

## Week 2 — Start the implementation

**Due Sunday, October 18, 2026, at noon Central.**

This week, all three groups will write and run code using HAM10000. You do not need to finish unrelated Week 1 writeups. Address anything needed for implementation while completing this week's tasks.

**Friday check-in:** October 16, 6–7 PM Central in Project Sync. Each group should demonstrate its progress and explain any blockers.

### Group 1: Data & Analysis

**Goal:** Check the dataset and create reproducible training, validation, and test splits.

Required:
- Load the metadata and locate images from both image folders.
- Check missing metadata, duplicate image IDs, missing images, and unreadable images.
- Report problems and document how you handle them without modifying the original data.
- Write code that generates train/validation/test manifests with a fixed random seed. Keep all images sharing a lesion_id in the same split.
- Report class counts for each split and verify that no lesion_id appears across splits.
- Correct the Week 1 explanation: lesion_id identifies an individual lesion, not a diagnosis category or patient.

**Talk to Modeling & Experiments about:**
- The split proportions and manifest columns before generating the splits.
- How to locate the images and load the generated manifests.
- One agreed seven-class label-to-index mapping.

**Talk to Explainability & App about:**
- How to access local sample images and look up their dataset labels.
- The agreed class mapping and readable class names.

**Submit:** Audit and split-generation code under src/data/, exploration under notebooks/, and findings/run instructions under docs/week2/.

Generated manifests belong locally under data/processed/ and must not be committed.

Suggested shared tasks: dataset audit; split generation and checks.

### Group 2: Modeling & Experiments

**Goal:** Build the image loader and verify that the model can complete one training step.

Required:
- Choose one pretrained CNN and briefly document the choice.
- Implement a loader that returns RGB image tensors and integer class labels.
- Use the class mapping agreed with Data & Analysis.
- Implement and document the chosen model's image resizing and normalization.
- Adapt the classifier to seven outputs.
- Using real training images, run a forward pass, calculate loss, perform backpropagation, and complete one optimizer step.
- Record the input/output shapes and confirm the loss is finite.

**Talk to Data & Analysis about:**
- Image locations, manifest format, split proportions, and class mapping.
- Any missing or unreadable images encountered by the loader.

Use their training manifest when available. While splits are being built, a temporary batch may be used to check the code, but do not report it as model evaluation.

**Talk to Explainability & App about:**
- The image-preparation code they should use before model predictions.
- The exact class order the model outputs.
- The planned model-loading and prediction interface.

Provide a reusable image-preparation function for predictions. Keep random training augmentation separate from that function.

**Submit:** Reusable code under src/ and setup/run instructions with training-step results under docs/week2/.

A full training run is not required.

Suggested shared tasks: image loader; model setup and training check.

### Group 3: Explainability & App

**Goal:** Build a working Streamlit prototype using real project images.

Required:
- Support image upload and selection of locally available HAM10000 samples.
- Display the image and show a clear message for unreadable files.
- Display the dataset label for selected HAM10000 samples, clearly labeled as the known dataset label rather than a prediction.
- Keep the educational-use notice visible.
- Prepare clearly labeled sections for future model predictions and Grad-CAM overlays.
- Mark predictions and heatmaps as pending until connected to the actual model.

**Talk to Data & Analysis about:**
- Local sample-image access and how to look up sample labels.
- The agreed class mapping and readable class names.

**Talk to Modeling & Experiments about:**
- The shared image-preparation function and how to use it.
- Model-output class order and the planned prediction interface.

Integrate their image-preparation function when available. Image upload and preview can be built before it is ready.

**Submit:** Application code under app/ and setup/run instructions under docs/week2/.

Working model predictions and Grad-CAM are not required this week. Do not display invented predictions or heatmaps.

Suggested shared tasks: image input and preview; layout, error handling, and preprocessing integration.

### GitHub and collaboration

- Complete the readiness checklist in your group's Discord channel and report access problems early.
- Use one task branch per task, not per person. Multiple members may collaborate on the same branch.
- Create task branches from the integration branch linked to your group's Week 2 issue. Use the actual new issue number; do not reuse Week 1 issue numbers for new assignments.
- Open task PRs into that integration branch. PMs review the combined integration PR into main.
- Coordinate file/notebook edits and identify each member's contribution in the PR.
- Include dependencies, data-path instructions, how to run the code, and evidence that it works on HAM10000.
- Have another member or PM review changes before merging.
- Record cross-group decisions in the relevant GitHub issues so everyone can find them.
- Keep raw data, generated datasets, and large model checkpoints out of GitHub.
- Use validation data for development decisions and keep the test set held out for final evaluation.

### Completion checklist

- [ ] Data & Analysis has runnable audit and split code with no lesion overlap.
- [ ] Modeling & Experiments has completed one successful training step on real images.
- [ ] Explainability & App has a working image-input and preview prototype.
- [ ] All groups use the same class mapping.
- [ ] Modeling and Explainability & App have agreed on prediction preprocessing and the model interface.
- [ ] Each group has submitted code through PRs, documented contributions, and reported remaining blockers.

## Week 1 — Quick team assignments

**Due Sunday, October 11, 2026, at noon Central.**

These assignments were intentionally small to help members get started. Work together on one submission per subteam, with an identifiable contribution from every member.

No trained model, working app, or completed Grad-CAM implementation is required this week.

### Team 1: Data & Analysis

**Submit:** notebooks/week1_data_exploration.ipynb

Include:
1. Code that loads the HAM10000 metadata.
2. A short explanation of the image_id, lesion_id, and dx columns.
3. A table or chart showing the number of images in each class.
4. Three observations about the dataset.
5. A short explanation of why images sharing a lesion_id must remain in the same train, validation, or test split.

Suggested division:
- Two members load the CSV and explain its columns.
- Two members produce and explain the class counts.
- One member writes the split explanation and checks that the notebook runs.
- Everyone adds an observation or explanation and reviews the shared output.

Only the metadata is needed for this week's assignment. Displaying sample images is optional.

### Team 2: Modeling & Experiments

**Submit:** docs/week1/modeling_plan.md

Include:
1. A short explanation of transfer learning in your own words.
2. One proposed pretrained CNN, such as ResNet or EfficientNet, and why it is a reasonable starting point.
3. An explanation of how the model would be adapted to seven lesion classes.
4. Two proposed evaluation metrics and what each measures.
5. An explanation of why overall accuracy alone could be misleading with uneven class sizes.

Suggested division:
- Two members explain transfer learning and adapting the classifier, and maybe researches a starting model as well.
- Two members explain evaluation metrics and class imbalance.

Include links to the sources you used. Installing PyTorch or training a model is optional this week.

### Team 3: Explainability & Application

**Submit:** docs/week1/demo_plan.md

Include:
1. A simple sketch of the proposed demo, embedded in or linked from the Markdown file.
2. The planned flow: image upload, prediction, and heatmap display.
3. A short explanation of Grad-CAM in your own words.
4. Two limitations of Grad-CAM.
5. A list of what the app will need from the other teams, including preprocessing, class order, and a trained model.
6. The educational-use notice that will appear in the demo.

Suggested division:
- Two members sketch the interface and explain its flow.
- Two members explain Grad-CAM and its limitations.
- One member documents the required inputs and educational-use notice.

Include links to the sources you used. Building the app is optional this week.

If access or GitHub problems prevent a contribution, contact a PM before the deadline.

## GitHub structure

We will use:
- notebooks/ for exploration and experiment notebooks.
- src/ for reusable Python code as implementation begins.
- app/ for the Streamlit application.
- docs/ for plans, findings, and documentation.
- data/ for local, Git-ignored datasets.

Folders will be added as files are needed.

README.md describes the project and setup. DATA.md documents data sources and access. DELIVERABLES.md records assignments and milestones. CONTRIBUTING.md defines the contribution workflow.

## Branches and pull requests

Follow CONTRIBUTING.md.

Each subteam's weekly assignment will have its own issue with owners, expected outputs, and completion criteria.

For an issue numbered N:
1. Create issue-N/integration from main.
2. Create task branches, which may be shared by members working together, from that integration branch, named `issue-N/task-slug` (for example, `issue-3/class-counts`).
3. Open task pull requests into issue-N/integration.
4. Have another member review the changes and address feedback before merging.
5. Open a pull request from issue-N/integration into main.
6. A PM reviews and approves the integration PR before it is merged.

Use the actual issue number in branch names. Subteams will use branches tied to assignments rather than permanent team branches.

Do not commit directly to main.

Every PR should include:
- The related issue number.
- A brief explanation of the contribution.
- How the work was checked.
- Any questions or remaining blockers.

Coordinate ownership of notebook cells and document sections before editing. Keep PRs focused and avoid unrelated file changes.

Notebooks must run from top to bottom and explain how to locate the required local data. Raw data and large model checkpoints must remain outside GitHub.

## Week 1 completion checklist

### Members
- [ ] Read the written Week 1 update and acknowledge it.
- [ ] Claim a task in the appropriate team issue.
- [ ] Make an identifiable GitHub contribution.
- [ ] Include a brief reflection in the team submission.
- [ ] Submit the team's required output by Sunday at noon Central.

### PMs
- [ ] Record subteam membership and task ownership.
- [ ] Document the initial dataset source and use terms in DATA.md.
- [ ] Verify that metadata and sample images can be loaded in code.
- [ ] Review team outputs and track contributions.
- [ ] Merge approved deliverables into main before the PM sync.
- [ ] Record attendance and share a recap.
- [ ] Complete the weekly report before Sunday's 5 PM PM sync.

## Semester roadmap

This is a working plan. Timing may change based on team progress, compute access, and the club's final presentation date.

| Week | Data & Analysis | Modeling & Experiments | Explainability & Application |
| --- | --- | --- | --- |
| 1 | Metadata exploration and class counts | Transfer-learning and evaluation plan | Demo sketch and Grad-CAM explanation |
| 2 | Dataset audit and lesion-grouped split code | Image loader, seven-class CNN, and one training step | Streamlit image viewer and shared prediction interface |
| 3 | Finish image audit and export verified existing splits; scope reduced to unblock training | Train one frozen-backbone baseline; validation macro F1 and confusion matrix | Finish Week 2 page and connect baseline predictions |
| 4 | Finish audit/split verification and analyze class imbalance/errors; catch-up counts toward this week | Correct the baseline pipeline and compare one focused improvement; scope reduced to finish integration | Connect real predictions and performance plots; Grad-CAM is optional while catching up |
| 5 | Examine errors by class and available metadata | Run controlled validation experiments | Integrate predictions and heatmaps |
| 6 | Document dataset limitations | Select model and assess calibration | Check heatmaps and test app behavior |
| 7 | Support final evaluation and analysis | Evaluate the locked model on the held-out test set | Complete demo and reproducibility checks |
| 8 | Final data documentation | Final evaluation writeup and model handoff | Final presentation and demonstration |

Use validation data for model selection. Keep the test set held out until final evaluation.

HAM10000 metadata provides lesion IDs, not patient IDs. Our initial split will be lesion-grouped, and we will document that limitation.

Changes to preprocessing, label order, or model interfaces must be coordinated across teams and recorded in GitHub.

## Final project deliverables

- Reproducible data preparation and split procedure.
- Trained classifier with documented preprocessing and class order.
- Evaluation report with per-class results and failure examples.
- Grad-CAM overlays with documented limitations.
- Streamlit demonstration app labeled for educational use.
- Setup instructions, final presentation, and project handoff.



