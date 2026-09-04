#!/bin/python3
# -*- coding: utf8 -*-

# MIT License

# Copyright (c) 2022 mehrdad
# Developed by mehrdad-mixtape https://github.com/mehrdad-mixtape/Pacman_Fetch

# Python Version 3.6 or higher
# Pacman_Fetch

"""Pacman Fetch -- a pacman themed, animated system fetch.

The module collects hardware and operating system information with
:mod:`psutil`, :mod:`distro` and a few external commands (``lscpu``, ``lspci``,
``xrandr``, ``ping``) and renders it as a coloured "fetch" panel built with
:mod:`rich`.  Command line switches are handled by the hand written parser in
:class:`Options` (``--help``, ``-v``, ``-d``, ``-p``, ``-i``, ``-c``).

Every collector writes its result into the module level :data:`outputs`
dictionary and :func:`main` prints that dictionary, key by key, in the order of
:data:`SYS_INFO_TITLE`.  The script is meant to be executed directly, so most
helpers communicate through module level globals instead of return values.

.. note::
    Linux and WSL are the supported platforms; macOS is untested.  A Nerd/Powerline
    patched font is required, otherwise the icons below render as boxes.

Example:
    .. code-block:: bash

        python3 __main__.py             # plain fetch
        python3 __main__.py -p -d 10    # pacman animation, typewriter speed 10
        python3 __main__.py -i -c       # ping the dns server of "config.json"

:var __repo__: URL of the upstream repository.
:vartype __repo__: str
:var __version__: Version string, including the coloured stability badge.
:vartype __version__: str
:var __project__: Project name used by the banners and the help page.
:vartype __project__: str
"""

BETA = "[red]beta[/]"
ALPHA = "[purple]alpha[/]"
STABLE = "[green]stable[/]"

__repo__ = "https://github.com/mehrdad-mixtape/Pacman_Fetch"
__version__ = f"v1.3.0-{STABLE}"
__project__ = "Pacman Fetch"

import os
import re
import sys
import json
import time
import random
import inspect
import itertools
import subprocess
import dataclasses

from typing import (
    Tuple, List, Dict, Union,
    Generator, Callable, Any
)

try:
    import psutil, distro
    from rich.box import HORIZONTALS
    from rich.text import Text
    from rich.table import Table
    from rich.console import Console
    from rich import pretty, traceback

    from threading import Thread

    # from bigtree.tree.construct import list_to_tree
    # from bigtree.tree.export import yield_tree

except ImportError as E:
    print(f"[*] Error. {E} - Please Install the Pkgs.")
    sys.exit()

else:
    pretty.install()
    traceback.install()

# Colors
# -------------------------------------------------------------------
SUPPORTED_COLOR = "red sea_green1 dark_orange medium_violet_red slate_blue3".split(' ') + \
"grey74 hot_pink gold1 dark_cyan blue purple chartreuse3 cyan orange4 white".split(' ') + \
"black green yellow grey66 salmon1".split(' ')

COLOR_BANNER = """{}{}{}{}{}{}{}
           {}{}{}{}{}{}{}"""

# Icons
# -------------------------------------------------------------------
GITHUB = '\uf113'
PYTHON = '\ue235'
HEART = '\uf004'
CPU = '\uf4bc'
BRAIN = '\ue28c'
LEGO = '\ue0ce'
SCREEN = '\ueb4c'
MEMORY = '\ue266'
SWAP = '\ue238'
DISK = '\ue240'
NETWORK = '\ueb3a'
UPTIME = '\uf0f4'
PING = '\uf0ec'
LINUX = '\uebc6'
HOTDOG = '\ue251'
DICE = '\ue270'
HAMBURGER = '\ue24d'

# Banners
# -------------------------------------------------------------------
BANNER = f"""
    ────━━━━ [blink][gold1]{__project__}[/][/] ━━━━────
        Version: {__version__}
        Source: {__repo__}
"""

MAIN_BANNER = f"""[bold][blink]┎─────────────────┒
            ║ {PYTHON} Pacmanfetch {GITHUB} ║
            ┖─────────────────┚[/][/]"""

# Functions
# -------------------------------------------------------------------
console = Console()
pprint = lambda *args, **kwargs: console.print(*args, **kwargs)

def clear() -> None:
    """Clear the terminal screen.

    Emits the ``ESC c`` (reset) sequence, which erases both the visible area and
    the scrollback on most modern emulators.  Called once from the ``__main__``
    guard, right before :func:`main` draws the fetch panel.
    """
    print('\033c', end='')


def goodbye(expression: bool, cause: str='Unknown'):
    """Abort the program when *expression* holds.

    The message is prefixed with the file name and line number of the *calling*
    frame, taken from :func:`inspect.getouterframes`, so the offending option or
    missing argument is easy to locate.

    :param expression: When truthy, print *cause* and exit; otherwise do nothing.
    :param cause: Reason printed together with the caller location.
    :raises SystemExit: Whenever *expression* is truthy.
    """
    if expression:
        pprint("{} {}#{}".format(
            cause,
            inspect.getouterframes(inspect.currentframe())[1].filename.split('/')[-1],
            inspect.getouterframes(inspect.currentframe())[1].lineno
        ))
        sys.exit()

# Decorators
# -------------------------------------------------------------------
def exception_handler(*exceptions, cause: str='', do_this: Callable=sys.exit) -> Callable[[Any], Any]:
    """Build a decorator that traps *exceptions* and runs an exit routine.

    The wrapper prints a coloured ``[Error]`` line and then calls *do_this*, which
    keeps the fetch output tidy instead of dumping a raw traceback.  When
    *exceptions* is empty the decorator is a no-op passthrough.

    :param exceptions: Exception classes caught by the wrapper.
    :param cause: Fixed message printed instead of the caught exception text.
    :param do_this: Callable invoked after the message; defaults to :func:`sys.exit`.
    :returns: A decorator that wraps a callable in the ``try``/``except`` block.
    :rtype: Callable[[Callable], Callable]

    .. warning::
        The wrapped function's return value is dropped whenever an exception is
        caught, so decorated collectors must report through :data:`outputs`.
    """
    def __decorator__(func: Callable) -> Callable[[Any], Any]:
        def __wrapper__(*args, **kwargs) -> Any:
            try:
                results = func(*args, **kwargs)
            except exceptions as err:
                if cause:
                    pprint(f"\n[{ERROR}]. {cause}")
                else:
                    pprint(f"\n[{ERROR}]. {err}")
                do_this()
            else:
                return results
        return __wrapper__
    return __decorator__

# Classes
# -------------------------------------------------------------------
class _NoValue:
    """Marker for "this option carries no glued input-argument".

    A private singleton, exposed as :data:`NO_VALUE`, used as the default of the
    ``attached_input`` parameter of :meth:`Options.__executer`. It exists to tell
    apart the two different meanings of an empty input-argument:

    * ``-g 1`` -> the value comes from the *next* ``sys.argv`` item.
    * ``-g1``  -> the value is *glued* to the option itself.

    ``None`` can not be used for this job because ``None`` is a legitimate
    :attr:`~Method.default_input` value, meaning "no default is available".

    :return: ``"<no-value>"``, so tracebacks and :func:`repr` stay readable.
    :rtype: str
    """
    __slots__ = ()

    def __repr__(self) -> str:
        return "<no-value>"


NO_VALUE = _NoValue()
"""The one and only :class:`_NoValue` instance.

Compared with ``is``, never with ``==``, so its identity is what carries the
meaning and it must never be re-created, unpickled or copied.
"""
# NOTE: this string literal after the assignment is not a stray comment: Sphinx
# autodoc picks up an expression's trailing string as its documentation, which is
# what makes `:data:`NO_VALUE`` resolvable from the rest of this module.


@dataclasses.dataclass(slots=True, eq=False, frozen=True)
class Method:
    """One command-line option together with the function that implements it.

    Built by :meth:`Options.__call__` for every decorated function and stored as
    the value of the :attr:`Options.option_method` mapping.

    :var do_this: the callback to run when its option is parsed.
    :vartype do_this: Callable[[Any], Any]
    :var has_input: ``True`` when the option expects an input-argument after it,
        like ``-g 1``.
    :vartype has_input: bool
    :var type_input: the callable that converts the raw command-line string into
        the value passed to :attr:`do_this`, for example :class:`int`. Only used
        when :attr:`has_input` is ``True``, where it is mandatory.
    :vartype type_input: type
    :var default_input: value used when the user gave no input-argument at all.
        ``None`` means "there is no fallback", which turns a missing
        input-argument into a fatal error.
    :vartype default_input: Any
    :var is_required: ``True`` when the option has to appear on the
        command-line.
    :vartype is_required: bool
    :var help_description: the text shown next to the option on the help screen.
    :vartype help_description: str
    """
    do_this: Callable[[Any], Any]
    has_input: bool
    type_input: type
    default_input: Any
    is_required: bool
    help_description: str


# NOTE: `eq=False` is what keeps this dataclass hashable, because generating
# `__eq__` would set `__hash__` to None. `frozen=True` makes a registered
# option impossible to mutate afterwards, so nothing can edit the registry
# behind `Options.option_method`, which is exposed as a read-only property.


class Options:
    """A dependency-free command-line argument parser.

    An alternative to :mod:`argparse` built around one idea: every option is a
    function, and the instance itself is the decorator that registers it. The
    object is callable, so ``option`` reads as both the registry and the
    decorator.

    **1.** Create the parser, then **2.** bind one function per option::

        option = Options("mytool")

        @option("-s", "--start")
        def do_you_wanna_start():
            ...

        @option("-o", "--opt", has_input=True, type_input=int, default_input=1)
        def do_you_wanna_optimize(arg: int):
            ...

        @option("-p", "--path", is_required=True)
        def do_you_wanna_pick_path():
            ...

    **3.** Read ``sys.argv`` and run whatever was asked for::

        for opt, output in option.parse():
            ...

    Short options may be bundled together, exactly like :mod:`getopt` does, and
    the bundled form is always equivalent to the spaced form::

        $ script.py -s -o 1     # options one by one
        $ script.py -so1        # bundle, equal to -os1 and -s -o 1
        $ script.py -o1         # input-argument glued to the option

    .. note::
        The keyword arguments of the decorator are **not** forwarded to the
        decorated function. They are stored on a :class:`Method` record and read
        back later by :meth:`__executer`.

    .. note::
        Registering an option that already exists, or parsing an unknown option,
        ends the whole process through :func:`~packages.utils.goodbye`.
        Errors are fatal by design: this parser never raises back to the caller.
    """

    __slots__ = ("project_name", "__option_method", "__run_without_help", "__intro", "__used")

    def __init__(self, project_name: str, intro: str='', run_without_help: bool=True):
        """Set up an empty registry that already knows ``--help``.

        :param project_name: name of the tool, used as the title of the help
            screen and in ``--help``'s own description.
        :type project_name: str
        :param intro: free text printed above the option table by ``--help``.
            Supports ``rich`` markup.
        :type intro: str
        :param run_without_help: when ``False``, calling the program with no
            arguments at all is an error instead of showing the help screen.
        :type run_without_help: bool
        """
        self.project_name = project_name
        self.__option_method: Dict[Tuple[str, ...], Method] = {
            ('--help',): Method(self.__help, False, None, None, False, f"Show help Screen of {project_name}")
        }
        self.__intro = intro
        self.__run_without_help = run_without_help
        self.__used: set = set()
        # NOTE: `--help` is seeded here so it can never be removed, and `__used`
        # records which option tuples the current command-line actually asked
        # for, so the `is_required` check at the end of `parse` can see options
        # that were hidden inside a bundle like `-so`.


    def __repr__(self):
        """Describe the parser by the command-line waiting to be parsed.

        :return: the live :data:`sys.argv` contents.
        :rtype: str
        """
        return f"Input Args: {sys.argv} to parse"


    def __call__(
            self, *options: str,
            has_input: bool=False,
            type_input: type=None,
            default_input: Any=None,
            is_required: bool=False,
            help_description: str="...",
        ):
        """Register a function as the implementation of one or more options.

        This is what makes the parser read as ``@option("-s", "--start")``: the
        :class:`Options` instance is called first to describe the option, and the
        decorator it hands back is then applied to the function.

        :param options: the aliases of this option, each starting with ``-`` or
            ``--``, for example ``"-s", "--start"``. They become the key of the
            option in the registry, so their order is only a display order.
        :type options: Tuple[str, ...]
        :param has_input: ``True`` when the option takes an input-argument after
            it, like ``-g 1``. The decorated function must then accept exactly
            one positional parameter.
        :type has_input: bool
        :param type_input: the callable that converts the raw command-line string
            into the value passed to the function, for example :class:`int`.
            Mandatory as soon as :paramref:`has_input` is ``True``.
        :type type_input: type
        :param default_input: value used when the user gave no input-argument.
            ``None`` means there is no fallback, so a missing input-argument
            becomes a fatal error.
        :type default_input: Any
        :param is_required: ``True`` to make this option mandatory on every run.
        :type is_required: bool
        :param help_description: the text shown next to the option on the help
            screen.
        :type help_description: str
        :return: the decorator that performs the registration.
        :rtype: Callable[[Callable[[Any], Any]], None]
        :raises SystemExit: if any of :paramref:`options` is already registered
            to another function.
        """
        def __decorator__(func: Callable[[Any], Any]) -> None:

            for exist_opt in self.__option_method:
                for opt in exist_opt:
                    goodbye(
                        opt in options,
                        cause="Duplicate option=({0}) selected for [bold]{1}[/], But now [bold]{2}[/] used for [bold]{3}[/]".format(
                            opt, func.__name__, opt, self.__option_method.get(exist_opt).do_this.__name__
                        )
                    )

            self.__option_method[options] = Method(func, has_input, type_input, default_input, is_required, help_description)

        return __decorator__
        # NOTE: `__decorator__` deliberately returns nothing, so `@option(...)`
        # rebinds the decorated name to `None`. The function survives only inside
        # the registry, which is why calling
        # `do_you_wanna_add_new_passwd()` directly from passgit.py would fail.
        # Do not "fix" this by returning `func` without checking all callers.


    @property
    def option_method(self) -> Dict[Tuple[str, ...], Method]:
        """The whole registry as a read-only view.

        :return: every registered option tuple mapped to its :class:`Method`.
        :rtype: Dict[Tuple[str, ...], Method]
        """
        return self.__option_method


    @property
    def all_options(self) -> List[str]:
        """Every single option alias, flattened.

        Every alias of every registered option is listed, so a tuple registered
        as ``("-p", "--passwd")`` contributes both ``-p`` and ``--passwd``. Used
        to recognise a bare option token that shows up where a value was
        expected, as in ``script.py -o -p``.

        :return: all aliases of all registered options.
        :rtype: List[str]
        """
        opt_lst: List[str] = []

        for option in self.option_method:
            for opt in option: opt_lst.append(opt)

        return opt_lst


    def __resolve(self, opt_argv: str) -> Union[Tuple[str, ...], None]:
        """Look up the registry key that a command-line token belongs to.

        Any one alias resolves to the same tuple, so short and long spellings are
        interchangeable::

            '-a'    ->  ('-a', '--add')
            '--add' ->  ('-a', '--add')
            '-z'    ->  None          # never registered

        :param opt_argv: one raw token taken from :data:`sys.argv`.
        :type opt_argv: str
        :return: the registered option tuple, or ``None`` when the token is not a
            known option. Returning ``None`` instead of raising lets
            :meth:`parse` tell "unknown option" apart from "bundle to expand".
        :rtype: Union[Tuple[str, ...], None]
        """
        for option in self.option_method:
            if opt_argv in option:
                return option

        return None


    def __bundle(self, opt_argv: str) -> List[Tuple[Tuple[str, ...], Any]]:
        """Split a bundle of short options into the single options it carries.

        Each item of the result is one option of the bundle, paired with the
        input-argument glued to it, or :data:`NO_VALUE` when nothing was glued::

            -ald    ->  [(-a, NO_VALUE), (-l, NO_VALUE), (-d, NO_VALUE)]
            -g3     ->  [(-g, '3')]
            -alg3   ->  [(-a, NO_VALUE), (-l, NO_VALUE), (-g, '3')]

        An option that needs an input-argument always terminates the bundle: the
        remaining characters become that input-argument instead of more options,
        which is what makes ``-ga`` mean ``-g a`` rather than ``-g -a``.

        :param opt_argv: a raw :data:`sys.argv` token known to start with a single
            ``-`` and not to be a registered option on its own.
        :type opt_argv: str
        :return: the bundle as ``(option tuple, attached input)`` pairs, in the
            order the user typed them.
        :rtype: List[Tuple[Tuple[str, ...], Any]]
        :raises SystemExit: if any character of the bundle is not a registered
            short option.

        .. note::
            The full list is built and validated *before* it is returned, so a
            bundle is all-or-nothing: ``-alz`` runs neither ``-a`` nor ``-l``.
            Returning a generator here would execute the leading valid options
            before the invalid one is ever reached.
        """
        bundle: List[Tuple[Tuple[str, ...], Any]] = []
        rest = opt_argv[1:]

        while rest:
            option = self.__resolve(f"-{rest[0]}")

            goodbye(
                option is None,
                cause=f"Invalid option=({opt_argv})"
            )

            rest = rest[1:]

            if self.option_method[option].has_input:
                bundle.append((option, rest if rest else NO_VALUE))
                return bundle

            bundle.append((option, NO_VALUE))

        return bundle


    def parse(self) -> Generator[Tuple[Tuple[str], Any], None, None]:
        """Walk :data:`sys.argv` and run every option the command-line asks for.

        This is the entry point of the parser. Each token is classified in
        exactly one of three ways:

        * a registered option, short or long -> run it on its own.
        * a token starting with ``--`` that is not registered -> fatal error,
          because long options can never be bundled.
        * any other ``-`` token -> hand it to :meth:`__bundle` and run each
          option it carries.

        Tokens that do not start with ``-`` are skipped silently: they are the
        input-arguments already consumed by the option in front of them, so
        ``-g 1`` must not try to parse the ``1`` as an option.

        :return: one ``(option tuple, value returned by the function)`` pair per
            executed option, in the order the user typed them.
        :rtype: Generator[Tuple[Tuple[str, ...], Any], None, None]
        :raises SystemExit: if the command-line is empty while
            ``run_without_help`` is ``False``, or if an option is unknown, or if
            a required option is missing.

        .. note::
            Being a generator, **nothing is executed until the result is
            iterated**. ``option.parse()`` on its own is a no-op; the consumer
            drives it, as ``main()`` in passgit.py does with
            ``for _ in option.parse(): ...``.
        """

        goodbye(
            len(sys.argv) < 2 and not self.__run_without_help,
            cause=f"Run program with --help for more information."
        )

        # Handle option validation and combination
        for i, opt_argv in enumerate(sys.argv, start=1):
            # NOTE: `i` is the 1-based position of the token, which is also the index of the
            # token *after* it, and that is exactly what `__executer` needs to read the
            # input-argument. Starting the count at 1 skips `sys.argv[0]`, the script name.
            if not opt_argv.startswith(('-', '--')):
                continue # valid options can start with - --

            goodbye( # if user enter just - or --
                opt_argv in ('-', '--'),
                cause=f"Invalid option=({opt_argv})"
            )

            # Handle the complete-options: Example ==> --add --list --dump
            # Handle the single-options: Example ==> -a -l -d
            option = self.__resolve(opt_argv)
            if option is not None:
                self.__used.add(option)
                yield self.__executer(option, i)
                continue

            # Long-options can not be bundled together: Example ==> --ald is invalid
            goodbye(
                opt_argv.startswith('--'),
                cause=f"Invalid option=({opt_argv})"
            )

            # Convert -ald to -a -l -d and parse it individually
            # Handle the abbreviation-options: Example ==> -a -l -d
            # Handle the mixed abbreviation-options: Example ==> -ald = -dal
            for option, attached_input in self.__bundle(opt_argv):
                self.__used.add(option)
                yield self.__executer(option, i, attached_input)

        # Handle is_required flag
        for option, method in self.option_method.items():
            if not method.is_required or option in self.__used:
                continue
            # NOTE: `__used` holds registry keys, not raw tokens, so a required option that
            # arrived bundled (like `-so`) still counts as used here.

            goodbye(
                True,
                cause="Input CMD: {0} <missing-option>\nThis missing-option=({1}) is Required, use --help to see".format(
                    ' '.join(sys.argv), ' '.join(option)
            ))


    def __executer(self, option: Tuple[str, ...], option_index: int, attached_input: Any=NO_VALUE) -> Tuple[Tuple[str, ...], Any]:
        """Run the function behind one option, converting its input-argument.

        :param option: the registry key, as returned by :meth:`__resolve`.
        :type option: Tuple[str, ...]
        :param option_index: the 1-based position of this option in
            :data:`sys.argv`, so ``sys.argv[option_index]`` is the token right
            after it, which is where an input-argument normally lives.
        :type option_index: int
        :param attached_input: the value glued to the option inside a bundle,
            like ``'3'`` for ``-g3``, or :data:`NO_VALUE` when the value has to
            come from :data:`sys.argv` instead.
        :type attached_input: Any
        :return: ``(option, value returned by the function)``. ``value`` is
            ``None`` for an option that needs no input-argument.
        :rtype: Tuple[Tuple[str, ...], Any]
        :raises SystemExit: when the option needs an input-argument that is
            missing, unusable, or has an inconsistent default.

        .. note::
            The ``except`` branches below are **not** error handling in the usual
            sense: they turn the three different ways an input-argument can go
            wrong into three different error messages, and each one either exits
            or falls back to :attr:`~Method.default_input`.
        """

        method: Method = self.option_method[option]
        output: Any = None

        if not method.has_input:
            return option, method.do_this()

        try:
            # Example ==> -g3 arrives already split by __bundle as attached_input='3',
            # while -g 3 arrives as NO_VALUE and must be read from the argv slot
            # right after the option, which is what `option_index` points at.
            arg_input = sys.argv[option_index] if attached_input is NO_VALUE else attached_input

            goodbye(
                method.type_input is None,
                cause=f"Get type-of-arguments=({arg_input}) after [bold]{option}[/]",
            )
            goodbye(
                method.default_input is not None
                and not isinstance(method.default_input, method.type_input),
                cause="Gave bad-default-argument=({0}) after [bold]{1}[/], type_input=[bold]{2}[/] & default_input=[bold]{3}[/] are inconsistent!".format(
                    method.default_input, option, method.type_input.__name__, method.default_input
            ))
            # Example ==> script.py -o -p, using the -o/--opt documented above.
            # The token after -o is a registered option rather than a value, so the
            # value was simply omitted: reuse default_input instead of handing '-p'
            # to type_input, which would only fail later as a confusing ValueError.
            if attached_input is NO_VALUE and arg_input in self.all_options:
                goodbye(
                    method.default_input is None,
                    cause=f"Not enough-argument after [bold]{option}[/], use --help for more information.",
                )
                goodbye(
                    not isinstance(method.default_input, method.type_input),
                    cause="Gave bad-default-argument=({0}) after [bold]{1}[/], type_input=[bold]{2}[/] & default_input=[bold]{3}[/] are inconsistent!".format(
                        method.default_input, option, method.type_input.__name__, method.default_input
                ))

                return option, method.do_this(method.type_input(method.default_input))

            arg_input = method.type_input(arg_input)
            output = method.do_this(arg_input)

        except IndexError:
            # NOTE: the option was the very last token, so `sys.argv[option_index]`
            # walked off the end of the list. Example ==> script.py -p -o
            goodbye(
                method.default_input is None,
                cause=f"Not enough-argument after [bold]{option}[/], use --help for more information.",
            )
            goodbye(
                not isinstance(method.default_input, method.type_input),
                cause="Gave bad-default-argument=({0}) after [bold]{1}[/], type_input=[bold]{2}[/] & default_input=[bold]{3}[/] are inconsistent!".format(
                    method.default_input, option, method.type_input.__name__, method.default_input
            ))

            # Example ==> script.py -p -o, using the -o/--opt documented above.
            # Nothing followed -o because it ended the command-line, which is what
            # raised IndexError, so reuse default_input here too.
            output = method.do_this(method.type_input(method.default_input))

        except ValueError:
            # NOTE: something did follow the option, but `type_input` refused to convert it.
            # Example ==> script.py -g abc, where int('abc') raises.
            # NOTE: unlike the other two fallbacks, this one passes `default_input` through
            # *without* running `type_input` on it. That asymmetry is pre-existing behaviour;
            # changing it could break a caller that relies on the raw default.
            goodbye(
                method.default_input is None,
                cause="Gave bad-argument=({0}) after [bold]{1}[/], type_input=[bold]{2}[/] & arg_input=[bold]{3}[/] are inconsistent!".format(
                    arg_input, option, method.type_input.__name__, arg_input
            ))

            output = method.do_this(method.default_input)

        except TypeError:
            # NOTE: reached when the registered function does not accept the single argument
            # this method tries to hand it, which always means `has_input=True` was declared
            # for a function that takes no parameter.
            goodbye(
                True,
                cause=f"You enabled [bold]has_input[/] for {method.do_this.__name__}(), Write input-argument for it"
            )

        return option, output


    def __help(self) -> None:
        """Print the help screen listing every registered option, then exit.

        This is the implementation seeded into the registry for ``--help`` by
        :meth:`~Options.__init__`, so it is reached through :meth:`__executer`
        like any other option rather than by a special case in :meth:`parse`.

        :return: nothing.
        :rtype: None
        :raises SystemExit: always, because help is the end of the program.
        """
        CYCLE_COLOR = itertools.cycle(SUPPORTED_COLOR)

        table = Table(
            "Options",
            "Required",
            # "Function",
            "Help",
            box=HORIZONTALS,
            title=f"""{self.project_name}""",
        )

        pprint(self.__intro)

        for option, method in self.option_method.items():
            # NOTE: colours are cycled per row purely so neighbouring rows stay readable.
            table.add_row(
                Text(' '.join(option), style=f"bold italic {next(CYCLE_COLOR)}"),
                Text('<<<-----' if method.is_required else '', style="bold"),
                # method.do_this.__name__,
                Text(method.help_description, justify=True),

            )

        pprint(table)
        sys.exit()
        # NOTE: each row is built with Text(), which does NOT parse rich markup, so a
        # help_description containing "[red]warn[/]" would print those tags literally. Keep
        # descriptions plain; markup is only honoured in the `intro` passed to Console.print.

# Blocks
# -------------------------------------------------------------------
F = "█"
E = "▒"

# Height and Width of Pacman & Ghost
# -------------------------------------------------------------------
W = 29
H = 12

# length of separator
# -------------------------------------------------------------------
D = 0

# Random Block color list
# -------------------------------------------------------------------
block_colors = ['[red]', '[purple]', '[dark_orange]', '[green]', '[cyan]']
random.shuffle(block_colors)

# Variables
# ---------------------------------------------------------------------
pacman_delay = lambda x=[]: 0
pacman_ping = False
pacman_config = False
INFO = '[green]Info[/]'
NOTICE = '[purple]Notice[/]'
WARNING = '[dark_orange]Warning[/]'
ERROR = '[red]Error[/]'
EXEC_ERROR = 'OS or Permission Error Occurred for Get {} Info'
threads: List[Thread] = []
outputs: Dict[str, str] = {
    'OS': '',
    'Kernel': '',
    'CPU': '',
    'GPU': '',
    'Display': '',
    'Memory': '',
    'Swap': '',
    'Disk': '',
    'Network': '',
    'UpTime': '',
}
limit = len(block_colors) + 1
try:
    terminal_width = os.get_terminal_size().columns
except OSError: # stdout is not a terminal: pipe, redirect, cron, CI, ...
    terminal_width = int(os.environ.get('COLUMNS', 80))
max_width = terminal_width // 29 # width of ghost
max_ghost = limit if max_width >= limit else max_width # How many ghost can place on terminal
config: Dict[str, str] = {}
rand_waits: List[int] = [0, 0, 0, 0, 0, 69, 69, 69, 69, 0, 0, 0, 0, 0]
progress_length = 20

# Options
# -------------------------------------------------------------------
option = Options(
    __project__,
    intro="""
    For Better Experience Install NerdFont: https://www.nerdfonts.com/
    """
)

@option(
    '-v', '--version',
    help_description=f"pacmanfetch -v. Show version of {__project__}."
)
def do_you_wanna_see_version() -> None:
    """Handle ``-v`` / ``--version``: print :data:`BANNER` and quit.

    :raises SystemExit: Always, raised by ``exit(0)`` right after the banner.
    """
    pprint(BANNER)
    exit(0)


@option(
    '-d', '--delay',
    has_input=True, type_input=int,
    help_description="pacmanfetch -d <0-...>. Type writer style printing"
)
def do_you_wanna_typewriter_style(speed: int) -> None:
    """Handle ``-d`` / ``--delay``: pick the typewriter printing speed.

    Replaces the :data:`pacman_delay` callable used by :func:`main` and
    :func:`do_you_wanna_show_pacman`; its result is divided by 3333 (or 369 for
    the animation) before being handed to :func:`time.sleep`.

    :param speed: Fixed delay in "ticks".  ``0`` keeps the default behaviour and
        randomises the pause through :data:`rand_waits` instead.
    """
    global pacman_delay
    if not speed:
        pacman_delay = random.choice
    else: pacman_delay = lambda x=[]: speed


@option(
    '-p', '--pacman',
    help_description="pacmanfetch -p. Show Pacman and Ghosts"
)
def do_you_wanna_show_pacman() -> None:
    """Handle ``-p`` / ``--pacman``: animate Pacman chasing the ghosts.

    Prints the :data:`PACMAN` and :data:`GHOST` blocks row by row, ``H`` rows in
    total.  The number of ghosts is capped by :data:`max_ghost`, which is derived
    from the terminal width, so narrow terminals simply show fewer of them.
    """
    ghost_buffer = "{}" * max_ghost 
    for n in range(H):
        pprint(ghost_buffer.format(
                PACMAN('[yellow]').split('\n')[n],
                *(GHOST(i).split('\n')[n] for i in range(max_ghost - 1)),
            )
        )
        time.sleep(pacman_delay(rand_waits) / 369)


@option(
    '-i', '--ping',
    help_description="pacmanfetch -i. Enable ping to check network connection"
)
def do_you_wanna_ping() -> None:
    """Handle ``-i`` / ``--ping``: enable the latency probe of :func:`ping`."""
    global pacman_ping
    pacman_ping = True


@option(
    '-c', '--config',
    help_description="pacmanfetch -c. Use \"config.json\" file"
)
def do_you_wanna_use_config() -> None:
    """Handle ``-c`` / ``--config``: load ``config.json`` next to this file.

    Fills the module level :data:`config` dictionary (``dns`` for :func:`ping`,
    ``gpu`` for :func:`gpu`) and creates the file with default values when it is
    missing, so a fresh clone works out of the box.
    """
    global pacman_config, config
    pacman_config = True

    config_path = os.path.dirname(os.path.abspath(__file__))
    if "config.json" in os.listdir(f"{config_path}/"):
        config_file = open(f"{config_path}/config.json", mode='r')
    else:
        default_conf = {
            "dns": "8.8.8.8",
            "gpu": "VGA"
        }
        with open(f"{config_path}/config.json", mode='w') as file:
            json.dump(default_conf, file)
        config_file = open(f"{config_path}/config.json", mode='r')
        pprint(f"[{NOTICE}]. config_file created!")

    config = json.load(config_file)
    
    config_file.close()


# OS logos
# -------------------------------------------------------------------
OS_name = distro.id()
OS_version = distro.version(pretty=True, best=True)

try:
    TTY = f" Term-({os.ttyname(sys.stdout.fileno())})"
except OSError: # no controlling terminal when the output is redirected
    TTY = " Term-(N/A)"

OS_logos = {
    # It is not compatible for all os, because of icon-fonts.
    'nixos': '\uf313', 'ubuntu': '\uf31b', 'debian': '\uf306',
    'raspbian': '\uf315', 'elementary': '\uf309', 'mint': '\uf30e',
    'centos': '\uf304', 'fedora': '\uf30a', 'redhat': '\uf316',
    'arch': '\uf303', 'manjaro': '\uf312', 'opensuse': '\uf314',
    'slackware': '\uf319', 'alpine': '\uf300', 'bsd': '\uf30c',
    'gentoo': '\uf30d', 'kali': '\uf327', 'deepin': '\uf321',
    'garuda': '\uf337'
}

# CPU Brand:
# -------------------------------------------------------------------
AMD = '[red]AMD[/red]:'
Intel = '[blue]Intel[/blue]'

# System Info Structure
# -------------------------------------------------------------------
SYS_INFO_TITLE: List[str] = [
    f"{OS_logos.get(OS_name, LINUX)}  OS      ",
    f"{HEART}  Kernel  ",
    f"{BRAIN}  CPU     ",
    f"{LEGO}  GPU     ",
    f"{SCREEN}  Display ",
    f"{MEMORY}  Memory  ",
    f"{SWAP}  Swap    ",
    f"{DISK}  Disk    ",
    f"{NETWORK}  Network ",
    f"{UPTIME}  UpTime  ",
]

NODE = "[bold][white]\ue683 {0}{1}  [/white][yellow2]\ue23f {2}[/yellow2][red]@[/red][cyan]{3}[/cyan][/bold]"

SEHLL_SYMS: Dict[str, str] = {
    'zsh': '%',
    'bash': '$',
}

# IP addresses
# -------------------------------------------------------------------
ifaces_addr: List[str] = []

# Pacman: Width=29, Height=12
# -------------------------------------------------------------------
MINI_PACMAN = '[yellow]󰮯 [/]  [dark_orange]󰊠 [/] [cyan]󰊠 [/] [red]󰊠 [/] [green]󰊠 [/]'
PACMAN = lambda ci: """
{0}▒▒▒▒▒▒▒▒█████████████▒▒▒▒▒▒▒▒[/]
{0}▒▒▒▒▒███████████████████▒▒▒▒▒[/]
{0}▒▒▒██████████████████████▒▒▒▒[/]
{0}▒█████████████████████▒▒▒▒▒▒▒[/]
{0}██████████████████▒▒▒▒▒▒▒▒▒▒▒[/]
{0}████████████████▒▒▒▒▒▒▒[/]
{0}██████████████████▒▒▒▒▒▒▒▒▒▒▒[/]
{0}▒█████████████████████▒▒▒▒▒▒▒[/]
{0}▒▒▒██████████████████████▒▒▒▒[/]
{0}▒▒▒▒▒███████████████████▒▒▒▒▒[/]
{0}▒▒▒▒▒▒▒▒█████████████▒▒▒▒▒▒▒▒[/]
""".format(ci).replace(E, ' ')

# Ghost: Width=29, Height=12
# -------------------------------------------------------------------
GHOST = lambda ci: """
{0}▒▒▒▒▒▒▒██████████████▒▒▒▒▒▒▒▒[/]
{0}▒▒▒▒▒██████████████████▒▒▒▒▒▒[/]
{0}▒▒▒@@@@@@█████@@@@@@█████▒▒▒▒[/]
{0}▒██@@##@@█████@@##@@███████▒▒[/]
{0}▒██####@@█████####@@███████▒▒[/]
{0}▒██@@@@@@█████@@@@@@███████▒▒[/]
{0}▒██████████████████████████▒▒[/]
{0}▒██████████████████████████▒▒[/]
{0}▒██████████████████████████▒▒[/]
{0}▒████▒▒████▒▒▒▒▒▒████▒▒████▒▒[/]
{0}▒██▒▒▒▒▒▒██▒▒▒▒▒▒██▒▒▒▒▒▒██▒▒[/]
""".format(block_colors[ci]).replace(E, ' ').replace('@', f"[white]{F}[/]").replace('#', f"[black]{F}[/]")


def cpu() -> None:
    """Collect the CPU model and its maximum frequency from ``lscpu``.

    Scans the ``Model name`` and ``CPU max MHz`` fields and stores
    ``" <model> <cores> Cores[ <freq> GHz]"`` in ``outputs['CPU']``.  The
    frequency is only appended for AMD processors, which is the upstream layout.

    .. note::
        Machines without a frequency report (some VMs and ARM boards print
        ``unknown``/``N/A`` instead of a number) fall back to ``0.0 GHz`` rather
        than aborting the whole fetch.
    """
    cpu_info = ''
    cpu_freq = 0.0
    cmd = 'lscpu'
    all_info = subprocess.check_output(cmd, shell=True).decode().strip()
    for line in all_info.split('\n'):
        if re.search('Model name', line):
            cpu_info = ''.join(re.sub(r".*Model name.*: *", '', line)).replace('CPU @ ', '')

        elif re.search('CPU max MHz', line):
            try:
                cpu_freq = float(''.join(re.sub(r".*CPU max MHz.*: *", '', line))) / 1000
            except ValueError: # non numeric value: keep cpu_freq at its default
                cpu_freq = 0.0
            break

    if 'AMD' in cpu_info:
        outputs['CPU'] = f" {cpu_info} {psutil.cpu_count()} Cores {cpu_freq:.1f} GHz"

    else:
        outputs['CPU'] = f" {cpu_info} {psutil.cpu_count()} Cores"


@exception_handler(RuntimeWarning, PermissionError, OSError, cause=EXEC_ERROR.format('Memory'))
def memory() -> None:
    """Collect RAM usage and store it in ``outputs['Memory']``.

    Bytes are converted with a decimal (1000 :sup:`3`) GB scale and the rounded
    usage percentage is mapped onto a bar of :data:`progress_length` blocks,
    ``━`` for the used and ``╍`` for the free part.

    .. note::
        ``RuntimeWarning``, ``PermissionError`` and ``OSError`` are turned into a
        single coloured error line by :func:`exception_handler`.
    """
    mem = psutil.virtual_memory()
    usage = round(mem.percent)
    total = round(mem.total / (1000 ** 3), 1)
    used =  round(abs(total - mem.available / (1000 ** 3)), 1)

    pu = usage * progress_length // 100
    pr = progress_length - pu

    outputs['Memory'] = f" Usage: [{'━' * pu}{'╍' * pr}] {usage:.2f}% =~ {used}GB / {total}GB"


@exception_handler(RuntimeWarning, PermissionError, OSError, cause=EXEC_ERROR.format('Swap'))
def swap() -> None:
    """Collect swap usage and store it in ``outputs['Swap']``.

    Same format as :func:`memory`, but the used amount is derived from the free
    swap instead of the available memory.  The local ``swap`` variable shadows this
    function while it runs, which is harmless as it never calls itself.
    """
    swap = psutil.swap_memory()
    usage = round(swap.percent)
    total = round(swap.total / (1000 ** 3), 1)
    used = round(abs(total - swap.free / (1000 ** 3)), 1)
    
    pu = usage * progress_length // 100
    pr = progress_length - pu

    outputs['Swap'] = f" Usage: [{'━' * pu}{'╍' * pr}] {usage:.2f}% =~ {used}GB / {total}GB"


@exception_handler(RuntimeWarning, PermissionError, OSError, cause=EXEC_ERROR.format('Disk'))
def disk() -> None:
    """Collect the size and free space of the ``/`` and ``/home`` mounts.

    Uses the binary (1024 :sup:`3`) GB scale and stores
    ``" Root(<size> GB) free: <free> GB ━ Home(<size> GB) free: <free> GB"`` in
    ``outputs['Disk']``.
    """
    home = psutil.disk_usage('/home')
    home_total = f"{home.total / (1024 ** 3):.1f}"
    home_free = f"{home.free / (1024 ** 3):.1f}"

    root = psutil.disk_usage('/')
    root_total = f"{root.total / (1024 ** 3):.1f}"
    root_free = f"{root.free / (1024 ** 3):.1f}"
    
    outputs['Disk'] = f""" Root({root_total} GB) free: {root_free} GB ━ Home({home_total} GB) free: {home_free} GB"""


def ping() -> str:
    """Measure the round-trip time to the configured DNS server.

    Runs ``ping -c 1 <dns> -i 0.1 -W 0.5`` and extracts the ``time=...`` field of
    the first reply.  The address is ``config['dns']`` when ``-c`` was given and
    ``8.8.8.8`` otherwise.

    :returns: ``"Ping: <rtt> <icon> <dns>"``, or ``"Ping: 999ms <icon> <dns>"``
        when no interface was detected or the command failed.
    :rtype: str

    .. note::
        Every failure is swallowed on purpose: an unreachable network must not
        stop the fetch, it only degrades the reported latency to ``999ms``.

    .. warning::
        The local ``time`` variable shadows the imported :mod:`time` module inside
        this function, so do not call :func:`time.sleep` here.
    """
    dns = config.get('dns', '8.8.8.8')
    cmd = f"ping -c 1 {dns} -i 0.1 -W 0.5"

    if not ifaces_addr:
        return f"Ping: 999ms {PING}  {dns}"

    else:
        try:
            with subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE) as ping_proc:
                stdout = ''.join(line.decode('utf-8') for line in ping_proc.stdout)
                time = re.findall(r"time=.*ms", stdout)[0].replace('time=', '')
                return f"Ping: {time} {PING}  {dns}"

        except Exception:
            return f"Ping: 999ms {PING}  {dns}"


def network() -> None:
    """Collect the IPv4 addresses of the interfaces (runs in a thread).

    Addresses are appended to :data:`ifaces_addr` and grouped by the first letter
    of the interface name:

    * ``t*``, ``n*``, ``wg*`` -> VPN, inserted at the front of the list,
    * ``e*``, ``u*``, ``d*``, ``b*`` -> wired,
    * ``w*`` -> wireless.

    The joined list is stored in ``outputs['Network']``; when nothing was found a
    "check your connections" hint is shown instead, followed by :func:`ping` if
    ``-i`` was requested.

    .. note::
        ``daemon=pacman_ping`` is evaluated once, at import time, so it is always
        :const:`False` here and the thread is joined before the panel is drawn.
    """
    try:
        net_ifaces = psutil.net_if_addrs()

        for interface_name, interface_addresses in net_ifaces.items():
            for address in filter(lambda addr: addr.family.name == "AF_INET", interface_addresses):
                if interface_name.startswith(('t', 'n', 'wg')):
                    ifaces_addr.insert(0, f" VPN 󰢭  ")

                elif interface_name.startswith(('e', 'u', 'd', 'b')):
                    ifaces_addr.append(f" {interface_name} 󱘖  {address.address} 󰈀  ")

                elif interface_name.startswith('w'):
                    ifaces_addr.append(f" {interface_name} 󱘖  {address.address}   ")

    except (RuntimeWarning, PermissionError, OSError):
        outputs['Network'] = f" Check your 󱘖  Connections 󰌙 {ping() if pacman_ping else ''}"

        return

    if not ifaces_addr:
        outputs['Network'] = f" Check your 󱘖  Connections 󰌙 {ping() if pacman_ping else ''}"

    else:
        outputs['Network'] = f"{'║'.join(ifaces_addr)} {ping() if pacman_ping else ''}"


def gpu() -> None:
    """Detect the GPU model(s) by parsing ``lspci`` (runs in a thread).

    ``VGA`` and ``3D`` controller lines are looked up per vendor and trimmed with
    a vendor specific pattern, then joined with ``━`` into ``outputs['GPU']``.
    Anything that cannot be recognised becomes ``" Unknown Vendor!"``.

    :returns: ``outputs['GPU']`` when the value is taken from the configuration
        file, otherwise :const:`None`.  Either way the :func:`threader` wrapper
        drops the value, the real output is the ``outputs`` entry.
    :rtype: str or None

    .. note::
        With ``-c`` the probe is skipped and ``config['gpu']`` is reported as it
        is, which is the documented way of handling a GPU this parser misses.
    """
    gpu_info = []

    if pacman_config:
        outputs['GPU'] = f" {config['gpu']}"
        return outputs['GPU']

    def extractor(brand: Dict[str, List[str]]) -> Generator[str, None, None]:
        """Yield the vendor name of every ``lspci`` line of *brand*.

        :param brand: Mapping of a vendor key (``AMD``, ``Intel``, ``NVIDIA``) to
            the ``lspci`` lines collected for it.
        :returns: One cleaned match per line; an empty string when the line does
            not fit the vendor pattern.
        :rtype: Generator[str, None, None]
        """
        patterns = {
            'AMD': r"\[AMD/ATI\] [a-zA-Z]*/?[a-zA-Z]*",
            'Intel': r"(U?HD Graphics [0-9]*?$)|(Iris Xe Graphics.*)",
            'NVIDIA': r"\[.*\].*"
        }
        for name, gpus in brand.items():
            for gpu in gpus:
                try:
                    yield re.search(patterns.get(name, r".*"), gpu) \
                        .group().replace('[', '').replace(']', '')

                except Exception:
                    yield ""

    stdout = subprocess.run('lspci', shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode('utf-8')

    amd: Dict[str, List[str]] = {'AMD': [
        *re.findall(r"VGA.*(\[AMD/ATI\].*) \(", stdout),
        *re.findall(r"3D.*(\[AMD/ATI\].*) \(", stdout),
        #*re.findall(r"Display.*(\[AMD/ATI\].*) \(", "Display controller [0830]: Advance, Inc. [AMD/ATI] lexa pro [Radeon RX 550/550X] [123:123] (rev c3)"),
        #"[AMD/ATI] Picasso/Raven 2 [Radeon Vega Series / Radeon Vega Mobile Series] (rev d2)",
        #"[AMD/ATI] Rembrandt (rev c8)",
    ]}
    intel: Dict[str, List[str]] = {'Intel': [
        *re.findall(r"VGA.*(Intel.*) \(", stdout),
        *re.findall(r"3D.*(Intel.*) \(", stdout),
    ]}
    nvidia: Dict[str, List[str]] = {'NVIDIA': [
        *re.findall(r"VGA.*(NVIDIA.*) \(", stdout),
        *re.findall(r"3D.*(NVIDIA.*) \(", stdout),
    ]}

    for brand in [amd, intel, nvidia]:
        for gpu in extractor(brand):
            gpu_info.append(f" {gpu} ")

    if not gpu_info:
        outputs['GPU'] = " Unknown Vendor!"

    else:
        outputs['GPU'] = '━'.join(gpu_info)


def operate() -> None:
    """Store the distribution name and version in ``outputs['OS']``.

    The values are read once at import time into :data:`OS_name` and
    :data:`OS_version` through :func:`distro.id` and :func:`distro.version`, so
    this collector only formats them (``" Ubuntu 22.04.1 (jammy)"``).
    """
    outputs['OS'] = f" {OS_name.title()} {OS_version}"


def kernel() -> None:
    """Store the kernel release, field 3 of :func:`os.uname`, in ``outputs['Kernel']``."""
    outputs['Kernel'] = f" {os.uname()[2]}"


def display() -> None:
    """Collect the active resolution and refresh rate of every monitor.

    ``xrandr`` is filtered down with ``awk`` to the mode marked as currently used
    (the one followed by ``*``) and each line becomes ``" DP-<res> <rate>Hz "``,
    joined with ``━`` into ``outputs['Display']``.

    :returns: :data:`TTY` when no usable mode could be read, otherwise
        :const:`None`.  The return value is only informative, the panel is fed by
        ``outputs['Display']``.
    :rtype: str or None

    .. note::
        ``xrandr`` is missing on Wayland only setups and inside plain TTYs, hence
        the fallback to the terminal name; with ``shell=True`` that failure shows
        up as :class:`subprocess.CalledProcessError`, not as
        :class:`FileNotFoundError`.
    """
    try:
        cmd = r"xrandr | awk 'match($0,/[0-9]*\.[0-9]*\*/)'"
        all_info = subprocess.check_output(
            cmd, shell=True, stderr=subprocess.DEVNULL
        ).decode().strip().split('\n')

        if not all_info[0]:
            outputs['Display'] = TTY
            return TTY

    except (FileNotFoundError, subprocess.CalledProcessError):
        outputs['Display'] = TTY
        return TTY

    else:
        displays = []
        for i, info in enumerate(all_info, start=1):
            resolution = info.split()[0]
            max_refresh_rate = max(
                [re.sub(r"(\*\+)|(\*)", '', ref) for ref in info.split()[1:]],
                key=len
            )
            displays.append(f" DP-{resolution} {max_refresh_rate}Hz ")

        outputs['Display'] = '━'.join(displays)
        # outputs['Display'] = displays


def node() -> str:
    """Build the ``shell% user@host`` prompt shown above the panel.

    The prompt character is looked up in :data:`SEHLL_SYMS` (``$`` for bash, ``%``
    for zsh, ``#`` for anything else or when the environment is minimal).

    :returns: The formatted :data:`NODE` template.
    :rtype: str

    .. warning::
        Side effect: sets the module level :data:`D`, the length of the separators
        drawn around the panel, to ``1.5 * len(shell + user + host)``.
    """
    global D

    shell = (os.environ.get('SHELL') or 'sh').split('/')[-1]
    shell_symbol = SEHLL_SYMS.get(shell, '#')
    user = os.environ.get('USER') or os.environ.get('LOGNAME') or 'unknown'
    host = os.uname()[1]

    D = int(len(shell + user + host) * 1.5)
    return NODE.format(shell, shell_symbol, user, host)


def uptime() -> None:
    """Store the time since boot as ``" <h>h <m>m <s>s"`` in ``outputs['UpTime']``.

    Computed from :func:`time.time` minus :func:`psutil.boot_time` and truncated to
    whole seconds; hours are deliberately not rolled over into days.
    """
    system_up = round(time.time() - psutil.boot_time())
    hours = system_up // 60 // 60
    minutes = system_up // 60 % 60
    seconds = system_up % 60

    outputs['UpTime'] = f" {hours}h {minutes}m {seconds}s"


@exception_handler(KeyboardInterrupt, cause=f"Ctrl+C", do_this=sys.exit)
def main() -> None:
    """Parse the command line, collect the system info and draw the panel.

    The workflow has three steps:

    1. drain the :meth:`Options.parse` generator, which executes every option
       given on the command line (``--help`` and ``-v`` exit from inside it),
    2. call the collectors, which fill the :data:`outputs` dictionary,
    3. print the prompt of :func:`node`, then one row per ``outputs`` entry --
       the title from :data:`SYS_INFO_TITLE` in the row colour of
       :data:`SUPPORTED_COLOR`, the value in plain text, both typed out character
       by character through :data:`pacman_delay` -- and finally the colour palette
       and the :data:`MAIN_BANNER` footer.

    .. note::
        Titles and colours are consumed in parallel with :func:`zip`, so the loop
        stops at the shorter of :data:`SUPPORTED_COLOR` and :data:`outputs`; an
        empty ``outputs`` value simply renders an empty row.

    :raises SystemExit: Raised by :func:`goodbye`/``sys.exit`` for unknown or
        duplicated options, and by the :func:`exception_handler` wrapper on
        ``Ctrl+C``.
    """
    global config

    # Argument parsing
    # -------------------------------------------------------------------
    for _ in option.parse(): ...

    # Call system info
    # -------------------------------------------------------------------
    operate()
    kernel()
    cpu()
    gpu()
    display()
    memory()
    swap()
    disk()
    network()
    uptime()

    # Draw system info
    # -------------------------------------------------------------------
    pprint(f"""
        {node()}
        {'─' * (D // 2 - 4)}╍╍╍╍━━━ {MINI_PACMAN}━━━╍╍╍╍{'─' * (D // 2 - 4)}""")

    for color, hw in zip(SUPPORTED_COLOR, outputs):
        try:
            details = outputs[hw]
            title = SYS_INFO_TITLE.pop(0)

        except IndexError:
            break

        else:
            pprint("         ║ ", end='')
            for char in title: # Type titles with color
                pprint(f"[{color}]{char}[/]", end='')
                time.sleep(pacman_delay(rand_waits) / 3333)

            pprint("║", end='')

            for char in details: # Type details without color
                pprint(f"{char}", end='')
                time.sleep(pacman_delay(rand_waits) / 3333)

            print()

    pprint(f"""        {'─' * (D // 2 - 4)}╍╍╍╍━━━ {MINI_PACMAN}━━━╍╍╍╍{'─' * (D // 2 - 4)}

          {COLOR_BANNER.format(*[f"[{color}]{E * 3}[/]" for color in SUPPORTED_COLOR])}
            [{random.choice(SUPPORTED_COLOR)}]{MAIN_BANNER}[/]""")


if __name__ == '__main__':
    clear()
    main()
