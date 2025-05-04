from behave import given, when, then
import subprocess

@given('un repositorio con packfile "{path}"')
def step_given_packfile(context, path):
    context.repo_path = path

@when('ejecuto "guardian scan {path}"')
def step_when_run_guardian_scan(context, path):
    result = subprocess.run(["python", "-m", "src.guardian", "scan", path],
                            capture_output=True, text=True)
    context.result = result

@then('el exit code es {code:d}')
def step_then_exit_code(context, code):
    assert context.result.returncode == code, f"Expected {code}, got {context.result.returncode}"


@then('la salida contiene "{mensaje}"')
def step_then_output_contains(context, mensaje):
    assert mensaje in context.result.stdout or mensaje in context.result.stderr, \
        f"'{mensaje}' no encontrado en la salida:\n{context.result.stdout}\n{context.result.stderr}"
