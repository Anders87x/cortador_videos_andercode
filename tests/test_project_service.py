import tempfile
import unittest
from pathlib import Path

from services.project_service import (
    get_project,
    register_project,
    update_project,
)


class ProjectServiceTest(unittest.TestCase):
    def test_new_project_uses_v1_defaults(self):
        with tempfile.TemporaryDirectory() as temp:
            projects_file = Path(temp) / "projects.json"

            project = register_project(
                projects_file,
                "curso-demo-abc123.mp4",
                "Curso Demo.mp4",
                1024,
            )

            self.assertEqual(project["output_format"], "vertical")
            self.assertTrue(project["branding_enabled"])
            self.assertEqual(
                project["branding_handle"],
                "anderson-bastidas.com",
            )
            self.assertEqual(project["hook_duration"], 0.5)
            self.assertEqual(project["outro_duration"], 5)

    def test_project_update_persists(self):
        with tempfile.TemporaryDirectory() as temp:
            projects_file = Path(temp) / "projects.json"

            project = register_project(
                projects_file,
                "curso-demo-abc123.mp4",
                "Curso Demo.mp4",
                1024,
            )

            update_project(
                projects_file,
                project["id"],
                hook_enabled=True,
                outro_enabled=True,
            )

            saved = get_project(projects_file, project["id"])

            self.assertTrue(saved["hook_enabled"])
            self.assertTrue(saved["outro_enabled"])


if __name__ == "__main__":
    unittest.main()
