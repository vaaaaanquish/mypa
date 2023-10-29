import click
from resolvelib import BaseReporter, Resolver
from build import ProjectBuilder

from .env import MypaEnv
from .locker import Locker
from .provider import Provider
from .pyproject import PyProjectToml

toml = PyProjectToml()


@click.group()
def cli():
    pass


@click.command()
def lock():
    dependencies = toml.get_mypa_dependencies()
    python_version = toml.get_python_version()
    resolver = Resolver(Provider(python_version), BaseReporter())

    click.echo("//---dependencies---")
    click.echo(dependencies)
    click.echo("//---python version---")
    click.echo(python_version)
    click.echo("//---resolve result---")
    resolve_dependencies_result = resolver.resolve(dependencies)
    for k, v in resolve_dependencies_result.mapping.items():
        click.echo(f"{k} = {v.version}")
    click.echo("//---lock---")
    click.echo("Writing mypa.lock ...")
    Locker.lock(resolve_dependencies_result.mapping)
    click.echo("//---[lock done!]---")


@click.command()
def install():
    dependencies = Locker.read()
    click.echo("//---dependencies---")
    for k, v in dependencies.items():
        click.echo(f'{k} = {v["version"]}')
    click.echo("//---make env---")
    python_version = toml.get_python_version()
    MypaEnv.create(python_version)
    click.echo("//---install dependencies---")
    for _, v in dependencies.items():
        MypaEnv.install(v['url'])
    click.echo("//---[install done!]---")


@click.command()
@click.argument('args', nargs=-1)
def run(args):
    click.echo('//---run---')
    MypaEnv.run(args)


@click.command()
def build():
    builder = ProjectBuilder('.', python_executable='.mypaenv/bin/python')
    for x in builder.build_system_requires:
        MypaEnv.install(x)
    builder.build('wheel', 'dist')


cli.add_command(lock)
cli.add_command(install)
cli.add_command(run)
cli.add_command(build)
