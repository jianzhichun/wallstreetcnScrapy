CREATE TABLE `wstable` (
  `id` CHAR(32) NOT NULL COMMENT 'uri+title+author md5编码id',
  `uri` VARCHAR(255) COMMENT 'uri',
  `title` VARCHAR(255) COMMENT '标题',
  `author` VARCHAR(255) COMMENT '作者',
  `time1` DATETIME COMMENT '时间',
  `description` TEXT COMMENT '描述',
  `content` TEXT COMMENT '内容',
  `images` TEXT COMMENT 'json uris',
  `view1` TEXT COMMENT 'view',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
select * from `wstable`;
DROP TABLE  `wstable`;
TRUNCATE TABLE `wstable`;
select count(*) from `wstable`