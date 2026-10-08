import unittest

from services.ffmpeg_service import (
    _build_branding_filters,
    _build_promo_filters,
    _video_encoder_args,
    balance_branding_title,
)


class FfmpegBuilderTest(unittest.TestCase):
    def test_promo_filter_uses_single_scale_and_pad(self):
        filters = _build_promo_filters(
            1,
            "hook",
            1080,
            1920,
            60,
            0.5,
            True,
        )

        graph = ";".join(filters)

        self.assertIn("scale=1080:1920", graph)
        self.assertIn("pad=1080:1920", graph)
        self.assertNotIn("split=2", graph)
        self.assertIn("fade=t=in", graph)
        self.assertIn("fade=t=out", graph)

    def test_branding_title_balances_like_preview(self):
        lines = balance_branding_title(
            "Crea una App Flutter que FUNCIONA SIN INTERNET + Firebase"
        )

        self.assertEqual(
            lines,
            [
                "Crea una App Flutter",
                "que FUNCIONA SIN",
                "INTERNET + Firebase",
            ],
        )

    def test_branding_filter_draws_shared_title_box(self):
        filters, output_label = _build_branding_filters(
            "basev",
            True,
            "Crea una App Flutter que FUNCIONA SIN INTERNET + Firebase",
            "anderson-bastidas.com",
        )

        graph = ";".join(filters)

        self.assertIn("drawbox=", graph)
        self.assertEqual(graph.count("brand_title_"), 6)
        self.assertIn("brand_handle", output_label)

    def test_cpu_encoder_args(self):
        args = _video_encoder_args("cpu")
        self.assertIn("libx264", args)

    def test_gpu_encoder_args(self):
        args = _video_encoder_args("gpu")
        self.assertIn("h264_nvenc", args)


if __name__ == "__main__":
    unittest.main()
