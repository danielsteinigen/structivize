import pytest

from tests.renderer_registry import RENDERER_REGISTRY


def generate_renderer_tool_cases():
    cases = []
    ids = []

    for renderer_info in RENDERER_REGISTRY:
        renderer_cls = renderer_info["renderer_cls"]

        renderer_instance = renderer_cls(code="")
        for tool in renderer_instance.tools:
            cases.append((renderer_info, tool))
            ids.append(f"{renderer_cls.__name__}-{tool}")

    return cases, ids


cases, case_ids = generate_renderer_tool_cases()


@pytest.mark.parametrize("renderer_info,tool", cases, ids=case_ids)
def test_renderer_rendering(renderer_info, tool, sample_file_factory, output_dir_factory, tmp_output_dir):
    renderer_cls = renderer_info["renderer_cls"]
    domain = renderer_info["domain"]
    renderer_name = renderer_info["renderer_name"]
    sample_filename = renderer_info["sample_filename"]

    sample_path = sample_file_factory(domain, renderer_name, sample_filename)
    output_base = output_dir_factory(domain, renderer_name, sample_filename)
    # output_base = tmp_output_dir / "output"

    renderer = renderer_cls(code_path=sample_path, output_base_path=output_base, output_format="png")

    response = renderer.render(tool)
    assert response.success, f"Render with tool {tool} failed for {renderer_cls.__name__}"
    print(response)

    expected_output = output_base.with_name(f"{output_base.name}_{tool}.{renderer.output_format}")
    assert expected_output.exists(), f"Expected output {expected_output} missing for {renderer_cls.__name__}"
