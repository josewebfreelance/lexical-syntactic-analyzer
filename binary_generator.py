def generate_binary(ir_string: str, target_linux: bool, target_windows: bool) -> dict:
    """
    Compila el IR a ejecutables nativos según las plataformas seleccionadas.
    Retorna dict con resultados para cada plataforma.
    """
    results = {}

    with tempfile.TemporaryDirectory() as tmpdir:
        ir_path = os.path.join(tmpdir, "program.ll")
        with open(ir_path, "w") as f:
            f.write(ir_string)

        if target_linux:
            results["linux"] = _compile_linux(ir_path, tmpdir)

        if target_windows:
            results["windows"] = _compile_windows(ir_path, tmpdir)

    return results