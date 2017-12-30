# Copyright (C) 2017 Braden Mitchell
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------------

from abc import ABCMeta, abstractmethod
from datetime import datetime
from lxml import etree

NS = {'ns': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
      'ns3': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2'}


class TCXParser(object):
    def __init__(self, tcx_file):
        root = self.get_root(tcx_file)
        if not root is None:
            self.time = Time(root)
            self.heartrate = HeartRate(root)
            self.distance = Distance(root)
            self.speed = Speed(root)
            self.cadence = Cadence(root)
            self.location = Location(root)
            self.altitude = Altitude(root)
            self.pace = Pace(self.time, self.distance)
            self.device = self.get_device_info(root)

    def get_root(self, tcx_file):
        if not tcx_file is None:
            if tcx_file.lower().endswith(('.tcx', '.xml')):
                with open(tcx_file, 'r') as f:
                    tree = etree.parse(f)
                    root = tree.xpath('/ns:TrainingCenterDatabase',
                                      namespaces=NS)[0]
                if not root is None:
                    return root.xpath('./ns:Activities/ns:Activity',
                                      namespaces=NS)[0]

    def get_device_info(self, root):
        device = root.xpath('./ns:Creator/ns:Name', namespaces=NS)[0].text
        t = root.xpath('./ns:Creator/ns:Version', namespaces=NS)[0]
        version = ('v' + t.xpath('./ns:VersionMajor', namespaces=NS)[0].text
                   + '.' + t.xpath('./ns:VersionMinor', namespaces=NS)[0].text)
        return device, version


class Measure(metaclass=ABCMeta):

    def get_data(self, root, var):
        if len(root.findall('./ns:Lap/ns:Track/ns:Trackpoint/ns:' + var,
                            namespaces=NS)):
            data = []
            for lap in root.xpath('./ns:Lap', namespaces=NS):
                for trkpt in lap.xpath('./ns:Track/ns:Trackpoint',
                                       namespaces=NS):
                    try:
                        data.append(float(trkpt.xpath('./ns:' + var,
                                                      namespaces=NS)[0].text))
                    except IndexError:
                        data.append(data[-1])
            return data

    def __repr__(self):
        return repr(self.data)

    def __iter__(self):
        yield from self.data

    def __getitem__(self, index):
        return self.data[index]

    def __len__(self):
        return len(self.data)


class Time(Measure):
    def __init__(self, root):
        self.data, abs_time = self.get_data(root)
        self.absolute = AbsTime(abs_time)

    def get_data(self, root):
        if len(root.findall('./ns:Lap/ns:Track/ns:Trackpoint/ns:Time',
                            namespaces=NS)):
            raw = []
            for lap in root.xpath('./ns:Lap', namespaces=NS):
                for trkpt in lap.xpath('./ns:Track/ns:Trackpoint',
                                       namespaces=NS):
                    try:
                        raw.append(datetime.strptime(str(trkpt.xpath(
                            './ns:Time', namespaces=NS)[0].text),
                            '%Y-%m-%dT%H:%M:%S.%fZ'))
                    except IndexError:
                        raw.append(data[-1])
            data = [x - raw[0] for x in raw]
            return data, raw

    def __repr__(self):
        return repr([repr(x) for x in self.data])

    def __str__(self):
        return str([str(x) for x in self.data])

    @property
    def duration(self):
        if self.data:
            return self.data[-1]

    @property
    def start(self):
        if self.data:
            return self.absolute[0]

    @property
    def finish(self):
        if self.data:
            return self.absolute[-1]


class AbsTime(Measure):
    def __init__(self, abs_time):
        self.data = abs_time

    def __repr__(self):
        return repr([repr(x) for x in self.data])

    def __str__(self):
        return str([str(x) for x in self.data])

    @property
    def start(self):
        if self.data:
            return self.data[0]

    @property
    def finish(self):
        if self.data:
            return self.data[-1]


class HeartRate(Measure):
    def __init__(self, root):
        var = 'HeartRateBpm/ns:Value'
        self.data = self.get_data(root, var)

    @property
    def min(self):
        if self.data:
            return min(self.data)

    @property
    def max(self):
        if self.data:
            return max(self.data)

    @property
    def average(self):
        if self.data:
            return sum(self.data) / len(self.data)


class Distance(Measure):
    def __init__(self, root):
        var = 'DistanceMeters'
        self.data = self.get_data(root, var)

    @property
    def raw(self):
        if self.data:
            cumdist = []
            for i, val in enumerate(self.data):
                if i == 0:
                    cumdist.append(val)
                else:
                    cumdist.append(val - sum(li))
            return cumdist

    @property
    def total(self):
        if self.data:
            return self.data[-1]


class Speed(Measure):
    def __init__(self, root):
        var = 'Extensions/ns3:TPX/ns3:Speed'
        self.data = self.get_data(root, var)

    @property
    def min(self):
        if self.data:
            return min(self.data)

    @property
    def max(self):
        if self.data:
            return max(self.data)

    @property
    def average(self):
        if self.data:
            return sum(self.data) / len(self.data)


class Cadence(Measure):
    def __init__(self, root):
        var = 'Extensions/ns3:TPX/ns3:RunCadence'
        self.data = self.get_data(root, var)

    @property
    def min(self):
        if self.data:
            return min(self.data)

    @property
    def max(self):
        if self.data:
            return max(self.data)

    @property
    def average(self):
        if self.data:
            return sum(self.data) / len(self.data)


class Location(Measure):
    def __init__(self, root):
        self.data = self.get_data(root)

    def get_data(self, root):
        if len(root.findall('./ns:Lap/ns:Track/ns:Trackpoint/ns:Position',
                            namespaces=NS)):
            data = []
            for lap in root.xpath('./ns:Lap', namespaces=NS):
                for trkpt in lap.xpath('./ns:Track/ns:Trackpoint',
                                       namespaces=NS):
                    try:
                        data.append((float(trkpt.xpath('./ns:Position/ns:LatitudeDegrees',
                                                       namespaces=NS)[0].text),
                                     float(trkpt.xpath('./ns:Position/ns:LongitudeDegrees',
                                                       namespaces=NS)[0].text)))
                    except IndexError:
                        data.append(data[-1])
            return data

    @property
    def start(self):
        if self.data:
            return self.data[0]

    @property
    def finish(self):
        if self.data:
            return self.data[-1]

    @property
    def latitude(self):
        if self.data:
            return [lat for lat, lon in self.data]

    @property
    def longitude(self):
        if self.data:
            return [lon for lat, lon in self.data]


class Altitude(Measure):
    def __init__(self, root):
        var = 'AltitudeMeters'
        self.data = self.get_data(root, var)

    @property
    def min(self):
        if self.data:
            return min(self.data)

    @property
    def max(self):
        if self.data:
            return max(self.data)

    @property
    def average(self):
        if self.data:
            return sum(self.data) / len(self.data)

    @property
    def change(self):
        if self.data:
            alt_delta = []
            for i, val in enumerate(self.data):
                if i == 0:
                    alt_delta.append(val - val)
                else:
                    alt_delta.append(val - self.data[i - 1])
            return alt_delta


class Pace(Measure):
    def __init__(self, _time, dist):
        self.data = self.get_data(_time, dist)

    def get_data(self, _time, dist):
        if _time and dist:
            pace = []
            for t, d in zip(_time, dist):
                pace.append((((t - _time[0]).seconds / 60) / (d / 1000)))
            return pace

    # def __repr__(self):
        # return repr([time.strftime('%M:%S', time.gmtime(x * 60)) for x in self.data])

    @property
    def seconds(self):
        if self.data:
            return [x * 60 for x in self.data]

    @property
    def min(self):
        if self.data:
            return max(self.data)

    @property
    def max(self):
        if self.data:
            li = [x for x in self.data if x > 0]
            return min(li)

    @property
    def average(self):
        if self.data:
            return self.data[-1]
