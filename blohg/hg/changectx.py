# -*- coding: utf-8 -*-
"""
    blohg.hg.changectx
    ~~~~~~~~~~~~~~~~~~

    Model with classes to represent Mercurial change context.

    :copyright: (c) 2010-2012 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from flask.helpers import locked_cached_property
from mercurial import hg

from blohg.hg.filectx import FileCtx


class ChangeCtxBase(object):
    """Base class that represents a change context."""

    def __init__(self, repo, ui):
        self._repo = repo
        self._ui = ui
        self._ctx = self._repo[self.revision_id]
        self.revno = self._ctx.rev()

    @property
    def revision_id(self):
        raise NotImplementedError

    @property
    def _extra_files(self):
        raise NotImplementedError

    @locked_cached_property
    def files(self):
        files = set(self._ctx.manifest().keys())
        try:
            files = files.union(set(self._extra_files))
        except NotImplementedError:
            pass
        return sorted(files)

    def needs_reload(self):
        raise NotImplementedError

    def get_filectx(self, path):
        return FileCtx(self._repo, self._ctx, path)


class ChangeCtxDefault(ChangeCtxBase):
    """Class with the specific implementation details for the change context
    of the default revision state of the repository. It inherits the common
    implementation from the class :class:`ChangeCtxBase`.
    """

    @property
    def revision_id(self):
        try:
            return self._repo.branchtags()['default']
        except Exception:
            return None

    def needs_reload(self):
        if self.revno is None:
            return True
        repo = hg.repository(self._ui, self._repo.root)
        try:
            revision_id = repo.branchtags()['default']
        except Exception:
            return True
        revision = repo[revision_id]
        return revision.rev() > self.revno


class ChangeCtxWorkingDir(ChangeCtxBase):
    """Class with the specific implementation details for the change context
    of the working dir revision state of the repository. It inherits the common
    implementation from the class :class:`ChangeCtxBase`.
    """

    revision_id = None

    @property
    def _extra_files(self):
        return self._repo.status(unknown=True)[4]

    def needs_reload(self):
        """This change context is mainly used by the command-line tool, and
        didn't provides any reliable way to evaluate its "freshness". Always
        reload.
        """
        return True