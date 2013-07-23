"""An interface for publishing rich data to frontends.

There are two components of the display system:

* Display formatters, which take a Python object and compute the
  representation of the object in various formats (text, HTML, SVG, etc.).
* The display publisher that is used to send the representation data to the
  various frontends.

This module defines the logic display publishing. The display publisher uses
the ``display_data`` message type that is defined in the IPython messaging
spec.

Authors:

* Brian Granger
"""

#-----------------------------------------------------------------------------
#       Copyright (C) 2008-2011 The IPython Development Team
#
#  Distributed under the terms of the BSD License.  The full license is in
#  the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

from __future__ import print_function

from IPython.config.configurable import Configurable
from IPython.utils import io
from IPython.utils.traitlets import List

#-----------------------------------------------------------------------------
# Main payload class
#-----------------------------------------------------------------------------

class DisplayPublisher(Configurable):
    """A traited class that publishes display data to frontends.

    Instances of this class are created by the main IPython object and should
    be accessed there.
    """

    def _validate_data(self, source, data, metadata=None):
        """Validate the display data.

        Parameters
        ----------
        source : str
            The fully dotted name of the callable that created the data, like
            :func:`foo.bar.my_formatter`.
        data : dict
            The formata data dictionary.
        metadata : dict
            Any metadata for the data.
        """

        if not isinstance(source, basestring):
            raise TypeError('source must be a str, got: %r' % source)
        if not isinstance(data, dict):
            raise TypeError('data must be a dict, got: %r' % data)
        if metadata is not None:
            if not isinstance(metadata, dict):
                raise TypeError('metadata must be a dict, got: %r' % data)

    def publish(self, source, data, metadata=None):
        """Publish data and metadata to all frontends.

        See the ``display_data`` message in the messaging documentation for
        more details about this message type.

        The following MIME types are currently implemented:

        * text/plain
        * text/html
        * text/latex
        * application/json
        * application/javascript
        * image/png
        * image/jpeg
        * image/svg+xml

        Parameters
        ----------
        source : str
            A string that give the function or method that created the data,
            such as 'IPython.core.page'.
        data : dict
            A dictionary having keys that are valid MIME types (like
            'text/plain' or 'image/svg+xml') and values that are the data for
            that MIME type. The data itself must be a JSON'able data
            structure. Minimally all data should have the 'text/plain' data,
            which can be displayed by all frontends. If more than the plain
            text is given, it is up to the frontend to decide which
            representation to use.
        metadata : dict
            A dictionary for metadata related to the data. This can contain
            arbitrary key, value pairs that frontends can use to interpret
            the data.  Metadata specific to each mime-type can be specified
            in the metadata dict with the same mime-type keys as
            the data itself.
        """

        # The default is to simply write the plain text data using io.stdout.
        if 'text/plain' in data:
            print(data['text/plain'], file=io.stdout)

    def clear_output(self, stdout=True, stderr=True, other=True):
        """Clear the output of the cell receiving output."""
        if stdout:
            print('\033[2K\r', file=io.stdout, end='')
            io.stdout.flush()
        if stderr:
            print('\033[2K\r', file=io.stderr, end='')
            io.stderr.flush()


class CapturingDisplayPublisher(DisplayPublisher):
    """A DisplayPublisher that stores"""
    outputs = List()

    def publish(self, source, data, metadata=None):
        self.outputs.append((source, data, metadata))
    
    def clear_output(self, stdout=True, stderr=True, other=True):
        super(CapturingDisplayPublisher, self).clear_output(stdout, stderr, other)
        if other:
            # empty the list, *do not* reassign a new list
            del self.outputs[:]


def publish_display_data(source, data, metadata=None):
    """Publish data and metadata to all frontends.

    See the ``display_data`` message in the messaging documentation for
    more details about this message type.

    The following MIME types are currently implemented:

    * text/plain
    * text/html
    * text/latex
    * application/json
    * application/javascript
    * image/png
    * image/jpeg
    * image/svg+xml

    Parameters
    ----------
    source : str
        A string that give the function or method that created the data,
        such as 'IPython.core.page'.
    data : dict
        A dictionary having keys that are valid MIME types (like
        'text/plain' or 'image/svg+xml') and values that are the data for
        that MIME type. The data itself must be a JSON'able data
        structure. Minimally all data should have the 'text/plain' data,
        which can be displayed by all frontends. If more than the plain
        text is given, it is up to the frontend to decide which
        representation to use.
    metadata : dict
        A dictionary for metadata related to the data. This can contain
        arbitrary key, value pairs that frontends can use to interpret
        the data. mime-type keys matching those in data can be used
        to specify metadata about particular representations.
        """
    from IPython.core.interactiveshell import InteractiveShell
    InteractiveShell.instance().display_pub.publish(
        source,
        data,
        metadata
    )


