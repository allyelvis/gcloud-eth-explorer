# -*- coding: utf-8 -*- #
# Copyright 2014 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""'logging write' command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from apitools.base.py import encoding
from googlecloudsdk.api_lib.logging import util
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.core import log


@base.UniverseCompatible
class Write(base.SilentCommand):
  """Write a log entry."""

  SEVERITY_ENUM = ('DEFAULT', 'DEBUG', 'INFO', 'NOTICE', 'WARNING',
                   'ERROR', 'CRITICAL', 'ALERT', 'EMERGENCY')

  PAYLOAD_TYPE = ('text', 'json')

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    parser.add_argument(
        'log_name', help=('Name of the log where the log entry will '
                          'be written.'))
    parser.add_argument(
        'message', help=('Message to put in the log entry. It can be '
                         'JSON if you include `--payload-type=json`.'))
    parser.add_argument(
        '--payload-type',
        choices=Write.PAYLOAD_TYPE, default='text',
        help=('Type of the log entry payload.'))
    parser.add_argument(
        '--severity', required=False,
        choices=Write.SEVERITY_ENUM, default='DEFAULT',
        help='Severity level of the log entry.')
    parser.add_argument(
        '--monitored-resource-type',
        default='global',
        help='Monitored Resource type to add to the payload',
    )
    parser.add_argument(
        '--monitored-resource-labels',
        type=arg_parsers.ArgDict(),
        metavar='KEY=VALUE, ...',
        default={},
        help='Monitored Resource labels to add to the payload',
    )

    util.AddParentArgs(parser, 'log entries to write')

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.
    """
    messages = util.GetMessages()

    severity_value = getattr(messages.LogEntry.SeverityValueValuesEnum,
                             args.severity.upper())

    monitored_resource = messages.MonitoredResource(
        type=args.monitored_resource_type
    )
    if args.monitored_resource_labels:
      monitored_resource.labels = encoding.PyValueToMessage(
          messages.MonitoredResource.LabelsValue, args.monitored_resource_labels
      )

    entry = messages.LogEntry(
        logName=util.CreateLogResourceName(
            util.GetParentFromArgs(args), args.log_name
        ),
        resource=monitored_resource,
        severity=severity_value,
    )

    if args.payload_type == 'json':
      json_object = util.ConvertToJsonObject(args.message)
      struct = messages.LogEntry.JsonPayloadValue()
      # Protobufs in Python do strict type-checking. We have to change the
      # type from JsonObject.Property to JsonPayloadValue.AdditionalProperty
      # even though both types have the same fields (key, value).
      struct.additionalProperties = [
          messages.LogEntry.JsonPayloadValue.AdditionalProperty(
              key=json_property.key,
              value=json_property.value)
          for json_property in json_object.properties
      ]
      entry.jsonPayload = struct
    else:
      entry.textPayload = args.message

    util.GetClient().entries.Write(
        messages.WriteLogEntriesRequest(entries=[entry]))
    log.status.write('Created log entry.\n')

Write.detailed_help = {
    'DESCRIPTION': """\
        {index}
        If the destination log does not exist, it will be created.
        By default, all log entries written with this command are written with
        the "global" resource type.

        {command} should be used for simple testing purposes.
        Check Cloud Logging agent for a proper way to send log entries:
        [](https://cloud.google.com/logging/docs/agent/)
    """,
    'EXAMPLES': """\
        To create a log entry in a given log, run:

          $ {command} LOG_NAME "A simple entry"

        To create a high severity log entry, run:

          $ {command} LOG_NAME "Urgent message" --severity=ALERT

        To create a structured log, run:

          $ {command} LOG_NAME '{"key": "value"}' --payload-type=json

        To create a log entry with a custom resource type, run:

          $ {command} LOG_NAME "A simple entry" --monitored-resource-type=gce_instance --monitored-resource-labels=zone=us-centra1-a,instance_id=1234
    """,
}
